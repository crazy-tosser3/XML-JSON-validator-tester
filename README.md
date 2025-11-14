# XML & JSON Validator

Приложение для валидации XML и JSON файлов с сохранением результатов в PostgreSQL базе данных. Быстрое развертывание через Docker и Docker Compose.

## Быстрый старт
Через Docker Compose (рекомендуется)

### Генерация Moc данных
Для генерации фейковых данных используйте комманду
```
uv run moc_data_gen.py
```
---
## Как запустить проект

### 1. Клонируйте репозиторий
```
git clone https://github.com/crazy-tosser3/XML-JSON-validator-tester.git
cd XML-JSON-validator-tester
```

### 2. Запустите контейнеры
```
docker compose up --build -d
```

### 3. Приложение будет доступно на:
+ http://localhost:8000
