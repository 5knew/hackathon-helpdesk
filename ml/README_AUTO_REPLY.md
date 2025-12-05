# Модуль Автоответа и FastAPI Сервис

## Описание

Модуль автоматического ответа на типовые вопросы использует семантический поиск (FAISS + Sentence-Transformers) для поиска подходящих шаблонов ответов.

## Структура

```
ml/
├── responses.json          # Шаблоны ответов на русском и казахском
├── auto_reply.py          # Модуль автоответа с FAISS
├── app.py                 # FastAPI сервис
├── models/                # Обученные модели
│   ├── classifier_category.pkl
│   ├── classifier_priority.pkl
│   ├── classifier_problem_type.pkl
│   └── sentence_transformer_model/
└── requirements.txt       # Зависимости
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Использование модуля автоответа

### Программное использование

```python
from auto_reply import AutoReplyService

# Инициализация сервиса
service = AutoReplyService(
    responses_path="responses.json",
    similarity_threshold=0.65  # Порог схожести (0-1)
)

# Проверка возможности автоответа
can_reply, response = service.can_auto_reply(
    query="Как сбросить пароль?",
    problem_type="Типовой",
    category="Общие вопросы"
)

if can_reply:
    print(f"Ответ: {response['text']}")
    print(f"Схожесть: {response['similarity']:.3f}")
```

### Запуск тестирования

```bash
python auto_reply.py
```

## Запуск FastAPI сервиса

### Локальный запуск

```bash
python app.py
```

Сервис будет доступен по адресу: `http://localhost:8000`

### С использованием uvicorn

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Кеширование FAISS индекса

- Индекс и метаданные автоматически сохраняются в `models/faiss_index.bin` и `models/faiss_index_meta.json`.
- При следующем запуске сервис использует кеш, если хеш `responses.json` совпадает. Это ускоряет старт и сохраняет консистентность.
- После обновления `responses.json` индекс перестроится автоматически.

## API Эндпоинты

### 1. `GET /` - Информация о сервисе

```bash
curl http://localhost:8000/
```

### 2. `GET /health` - Проверка работоспособности

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "auto_reply_available": true
}
```

### 3. `POST /predict` - Классификация тикета

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Не могу войти в систему, забыл пароль",
    "subject": "Проблема с входом"
  }'
```

Ответ:
```json
{
  "category": "Общие вопросы",
  "priority": "Низкий",
  "problem_type": "Типовой",
  "confidence": {
    "category": 0.95,
    "priority": 0.88,
    "problem_type": 0.92
  }
}
```

### 4. `POST /auto_reply` - Автоматический ответ

```bash
curl -X POST "http://localhost:8000/auto_reply" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Как сбросить пароль?",
    "problem_type": "Типовой",
    "category": "Общие вопросы"
  }'
```

Ответ:
```json
{
  "can_auto_reply": true,
  "response_text": "Для сброса пароля перейдите по ссылке...",
  "response_id": "password_reset",
  "similarity": 0.87,
  "category": "Общие вопросы",
  "language": "ru"
}
```

### 5. `POST /predict_and_reply` - Комбинированный эндпоинт

Выполняет классификацию и пытается дать автоответ:

```bash
curl -X POST "http://localhost:8000/predict_and_reply" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Когда нужно оплачивать счет?",
    "subject": "Вопрос по оплате"
  }'
```

## Логика автоответа

Модуль определяет возможность автоответа на основе:

1. **Тип проблемы**: Автоответ возможен только для типовых проблем (`problem_type == "Типовой"`)
2. **Семантическое сходство**: Запрос должен иметь схожесть >= `similarity_threshold` (по умолчанию 0.65) с одним из шаблонов
3. **Язык**: Ответ выбирается на том же языке, что и запрос (автоопределение или явное указание)
4. **Категория**: Опциональная фильтрация по категории тикета

## Добавление новых шаблонов ответов

Отредактируйте файл `responses.json`:

```json
{
  "responses": [
    {
      "id": "unique_id",
      "category": "Категория",
      "keywords": ["ключевое", "слово"],
      "ru": "Ответ на русском языке",
      "kz": "Жауап қазақ тілінде"
    }
  ]
}
```

После добавления новых шаблонов перезапустите сервис - индекс FAISS будет перестроен автоматически.

## Параметры настройки

### AutoReplyService

- `similarity_threshold` (float, default=0.65): Минимальная схожесть для автоответа (0-1)
- `responses_path` (str): Путь к файлу с шаблонами ответов
- `model_path` (str, optional): Путь к модели sentence-transformers

### Порог схожести

- **0.7-0.9**: Высокий порог - только очень похожие запросы получат автоответ
- **0.5-0.7**: Средний порог (рекомендуется) - баланс между точностью и покрытием
- **0.3-0.5**: Низкий порог - больше запросов получат автоответ, но возможны неточности

## Производительность

- **Время ответа**: ~50-200ms на запрос (зависит от размера индекса)
- **Память**: ~200-500MB (зависит от количества шаблонов и модели)
- **Масштабируемость**: FAISS индекс может обрабатывать миллионы векторов

## Troubleshooting

### Ошибка: "Модели не загружены"

Убедитесь, что вы обучили модели:
```bash
python train_classifiers.py
```

### Ошибка: "Сервис автоответа недоступен"

Проверьте наличие файла `responses.json` в директории `ml/`

### Низкая точность автоответа

1. Увеличьте `similarity_threshold`
2. Добавьте больше релевантных шаблонов в `responses.json`
3. Проверьте качество шаблонов ответов

## Интеграция с Backend

Backend должен вызывать ML сервис следующим образом:

```python
import requests

# Классификация
response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "Текст тикета", "subject": "Тема"}
)
prediction = response.json()

# Автоответ (если problem_type == "Типовой")
if prediction["problem_type"] == "Типовой":
    auto_reply = requests.post(
        "http://localhost:8000/auto_reply",
        json={
            "text": "Текст тикета",
            "category": prediction["category"],
            "problem_type": prediction["problem_type"]
        }
    )
    reply_data = auto_reply.json()
    
    if reply_data["can_auto_reply"]:
        # Отправить автоответ пользователю
        send_response_to_user(reply_data["response_text"])
```

## Документация API

После запуска сервиса доступна интерактивная документация:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

