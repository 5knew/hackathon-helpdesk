# Быстрый старт - Модуль автоответа

## Шаг 1: Установка зависимостей

```bash
cd ml
pip install -r requirements.txt
```

## Шаг 2: Обучение моделей (если еще не обучены)

```bash
# Подготовка датасета
python prepare_dataset.py

# Обучение классификаторов
python train_classifiers.py
```

## Шаг 3: Тестирование модуля автоответа

```bash
python auto_reply.py
```

## Шаг 4: Запуск FastAPI сервиса

```bash
python app.py
```

Сервис будет доступен по адресу: `http://localhost:8000`

## Шаг 5: Проверка работоспособности

```bash
# Проверка здоровья сервиса
curl http://localhost:8000/health

# Тест классификации
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Не могу войти в систему"}'

# Тест автоответа
curl -X POST "http://localhost:8000/auto_reply" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Как сбросить пароль?",
    "problem_type": "Типовой",
    "category": "Общие вопросы"
  }'
```

## Документация API

После запуска откройте в браузере:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура файлов

- `responses.json` - шаблоны ответов
- `auto_reply.py` - модуль автоответа
- `app.py` - FastAPI сервис
- `models/` - обученные модели (создаются после обучения)

