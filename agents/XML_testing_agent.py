import time
from lxml import etree

def XMLloadfile(xml_path: str):
    """Загружает XML файл"""
    with open(xml_path, 'rb') as f:
        return etree.parse(f)

def XMLvalidate(xml_path: str, xslt_path: str = None):
    """
    Применяет XSLT трансформацию к XML
    Возвращает результат без дополнительной валидации
    """
    start_time = time.time()
    try:
        xml = XMLloadfile(xml_path)
        xslt = etree.parse(xslt_path)
        transform = etree.XSLT(xslt)
        
        result = transform(xml)
        
        result_tree = etree.fromstring(str(result).encode('utf-8'))
        errors = []
        
        for item in result_tree.findall('.//item'):
            validation = item.find('validation')
            if validation is not None:
                for error in validation.findall('error'):
                    if error.text:
                        name_elem = item.find('name')
                        name = name_elem.text if name_elem is not None else "Unknown"
                        errors.append(f"[{name}] {error.text}")
        
        validation_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "valid" if len(errors) == 0 else "invalid",
            "errors": errors,
            "validation_time_ms": validation_time_ms
        }
        
    except Exception as e:
        validation_time_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "error",
            "errors": [str(e)],
            "validation_time_ms": validation_time_ms
        }

if __name__ == '__main__':
    result = XMLvalidate("data.xml", "validator.xsl")
    print(f"Статус: {result['status']}")
    print(f"Ошибок: {len(result['errors'])}")
    print(f"Время: {result['validation_time_ms']} мс")
    if result['errors']:
        for error in result['errors']:
            print(f" - {error}")
