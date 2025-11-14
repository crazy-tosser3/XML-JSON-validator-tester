from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    Float,
    DateTime,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://validator:1234@localhost:5432/validation_db"
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ValidationResult(Base):
    """Модель результата валидации"""

    __tablename__ = "validation_results"

    id = Column(Integer, primary_key=True, index=True)
    validation_type = Column(String(10), nullable=False, index=True)
    input_file_name = Column(String(255))
    is_valid = Column(Boolean, nullable=False, index=True)
    execution_time_ms = Column(Float, nullable=False)
    error_count = Column(Integer, default=0)
    errors = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    """Инициализация БД"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ База данных инициализирована")
    except Exception as e:
        logger.error(f"✗ Ошибка инициализации БД: {e}")


def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
