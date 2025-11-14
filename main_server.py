from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import sys
import time
import logging
from datetime import datetime
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "agents"))

try:
    from JSON_testing_agent import JSONvalidate
    JSON_AVAILABLE = True
except ImportError as e:
    JSON_AVAILABLE = False
    logger.error(f"JSON_testing_agent: {e}")

try:
    from XML_testing_agent import XMLvalidate
    XML_AVAILABLE = True
except ImportError as e:
    XML_AVAILABLE = False
    logger.error(f"XML_testing_agent: {e}")

from database import init_db, get_db, ValidationResult

init_db()

app = FastAPI(title="XML & JSON Validator")


tests_db = {}

def get_stats(db, v_type):
    """Получить статистику по типу валидации"""
    result = db.query(
        func.avg(ValidationResult.execution_time_ms).label("avg"),
        func.count(ValidationResult.id).label("count")
    ).filter(ValidationResult.validation_type == v_type).first()
    
    valid = db.query(func.count(ValidationResult.id)).filter(
        ValidationResult.validation_type == v_type,
        ValidationResult.is_valid == True
    ).scalar() or 0
    
    invalid = db.query(func.count(ValidationResult.id)).filter(
        ValidationResult.validation_type == v_type,
        ValidationResult.is_valid == False
    ).scalar() or 0
    
    total = result.count or 0
    return {
        "avg_time_ms": round(result.avg, 2) if result.avg else 0,
        "total_count": total,
        "valid_count": valid,
        "invalid_count": invalid,
        "valid_percentage": round(valid / total * 100, 2) if total else 0
    }

@app.get("/")
async def home(db: Session = Depends(get_db)):
    """Главная - JSON метрики"""
    try:
        return {
            "message": "Панель валидации XML/JSON",
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "validators": {
                "JSON": {"status": "active" if JSON_AVAILABLE else "inactive"},
                "XML": {"status": "active" if XML_AVAILABLE else "inactive"}
            },
            "database": {"status": "connected"},
            "metrics": {
                "json": get_stats(db, "json"),
                "xml": get_stats(db, "xml")
            },
            "endpoints": {
                "validate_json": "/validate/json",
                "validate_xml": "/validate/xml",
                "results_json": "/results/json",
                "results_xml": "/results/xml",
                "testing_result": "/testing/res/{uuid}",
                "stats": "/stats",
                "health": "/health"
            }
        }
    except Exception as e:
        logger.error(f"Ошибка статистики: {e}")
        raise HTTPException(500, str(e))

@app.post("/validate/json")
async def validate_json(file_path: str = "data.json", db: Session = Depends(get_db)):
    """Валидация JSON"""
    if not JSON_AVAILABLE:
        raise HTTPException(503, "JSON валидатор недоступен")
    if not os.path.exists(file_path):
        raise HTTPException(404, f"Файл не найден: {file_path}")
    
    uuid = str(uuid4())
    start_time = time.time()
    
    try:
        result = JSONvalidate(file_path)
        total_time_ms = (time.time() - start_time) * 1000
        
        db_result = ValidationResult(
            validation_type="json",
            input_file_name=os.path.basename(file_path),
            is_valid=result.get("status") == "valid",
            execution_time_ms=result.get("validation_time_ms", 0),
            error_count=len(result.get("errors", [])),
            errors="\n".join(result.get("errors", [])) if result.get("errors") else None
        )
        db.add(db_result)
        db.commit()
        
        tests_db[uuid] = {
            "test_type": "json",
            "status": result.get("status"),
            "file_path": file_path,
            "errors": result.get("errors", []),
            "validation_time_ms": result.get("validation_time_ms", 0),
            "server_time_ms": round(total_time_ms, 2)
        }
        
        return {
            "test_uuid": uuid,
            "test_type": "json",
            "status": result.get("status"),
            "errors_count": len(result.get("errors", [])),
            "validation_time_ms": result.get("validation_time_ms", 0),
            "server_processing_time_ms": round(total_time_ms, 2),
            "errors": result.get("errors", [])[:10]
        }
    except Exception as e:
        logger.error(f"JSON ошибка: {e}")
        raise HTTPException(500, str(e))

@app.post("/validate/xml")
async def validate_xml(file_path: str = "data.xml", db: Session = Depends(get_db)):
    """Валидация XML"""
    if not XML_AVAILABLE:
        raise HTTPException(503, "XML валидатор недоступен")
    if not os.path.exists(file_path):
        raise HTTPException(404, f"Файл не найден: {file_path}")
    
    uuid = str(uuid4())
    start_time = time.time()
    
    try:
        xslt_path = "validator.xsl" if os.path.exists("validator.xsl") else None
        result = XMLvalidate(file_path, xslt_path)
        total_time_ms = (time.time() - start_time) * 1000
        
        db_result = ValidationResult(
            validation_type="xml",
            input_file_name=os.path.basename(file_path),
            is_valid=result.get("status") == "valid",
            execution_time_ms=result.get("validation_time_ms", 0),
            error_count=len(result.get("errors", [])),
            errors="\n".join(result.get("errors", [])) if result.get("errors") else None
        )
        db.add(db_result)
        db.commit()
        
        tests_db[uuid] = {
            "test_type": "xml",
            "status": result.get("status"),
            "file_path": file_path,
            "errors": result.get("errors", []),
            "validation_time_ms": result.get("validation_time_ms", 0),
            "server_time_ms": round(total_time_ms, 2)
        }
        
        return {
            "test_uuid": uuid,
            "test_type": "xml",
            "status": result.get("status"),
            "errors_count": len(result.get("errors", [])),
            "validation_time_ms": result.get("validation_time_ms", 0),
            "server_processing_time_ms": round(total_time_ms, 2),
            "errors": result.get("errors", [])[:10]
        }
    except Exception as e:
        logger.error(f"XML ошибка: {e}")
        raise HTTPException(500, str(e))

@app.get("/testing/res/{test_uuid}")
def get_test_result(test_uuid: str):
    """Получить результат по UUID"""
    if test_uuid not in tests_db:
        raise HTTPException(404, f"Результат {test_uuid} не найден")
    
    data = tests_db[test_uuid]
    return {
        "test_uuid": test_uuid,
        "test_type": data["test_type"],
        "status": data["status"],
        "file_path": data.get("file_path"),
        "errors_count": len(data["errors"]),
        "errors": data["errors"],
        "validation_time_ms": data["validation_time_ms"],
        "server_time_ms": data["server_time_ms"]
    }

@app.get("/results/json")
async def results_json(db: Session = Depends(get_db)):
    """Результаты JSON"""
    results = db.query(ValidationResult).filter(
        ValidationResult.validation_type == "json"
    ).order_by(ValidationResult.created_at.desc()).limit(100).all()
    
    return {
        "validation_type": "json",
        "total_results": len(results),
        "results": [{
            "id": r.id,
            "file_name": r.input_file_name,
            "is_valid": r.is_valid,
            "execution_time_ms": r.execution_time_ms,
            "error_count": r.error_count,
            "errors": r.errors.split("\n") if r.errors else [],
            "created_at": r.created_at.isoformat()
        } for r in results]
    }

@app.get("/results/xml")
async def results_xml(db: Session = Depends(get_db)):
    """Результаты XML"""
    results = db.query(ValidationResult).filter(
        ValidationResult.validation_type == "xml"
    ).order_by(ValidationResult.created_at.desc()).limit(100).all()
    
    return {
        "validation_type": "xml",
        "total_results": len(results),
        "results": [{
            "id": r.id,
            "file_name": r.input_file_name,
            "is_valid": r.is_valid,
            "execution_time_ms": r.execution_time_ms,
            "error_count": r.error_count,
            "errors": r.errors.split("\n") if r.errors else [],
            "created_at": r.created_at.isoformat()
        } for r in results]
    }

@app.get("/stats")
async def stats(db: Session = Depends(get_db)):
    """Статистика"""
    return {
        "json": get_stats(db, "json"),
        "xml": get_stats(db, "xml")
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check"""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("Запуск сервера")
    logger.info(f"JSON: {'Да' if JSON_AVAILABLE else 'Нет'}")
    logger.info(f"XML: {'Да' if XML_AVAILABLE else 'Нет'}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
