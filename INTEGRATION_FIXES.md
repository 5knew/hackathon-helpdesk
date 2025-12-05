# Исправления интеграции Backend и ML сервиса

## Внесенные изменения

### 1. Исправлен `backend/services/ai_classifier.py`
**Проблема**: Backend отправлял `{"subject": str, "body": str}`, а ML сервис (`app.py`) ожидает `{"text": str, "subject": Optional[str]}`

**Решение**: Изменен формат запроса:
```python
# Было:
payload = {
    "subject": subject or "Заявка",
    "body": body
}

# Стало:
full_text = f"{subject or ''} {body}".strip()
payload = {
    "text": full_text,
    "subject": subject or ""
}
```

### 2. Исправлен `backend/services/auto_resolver.py`
**Проблема 1**: Backend ожидал поле `reply`, а ML сервис возвращает `response_text`

**Решение**: Изменено получение ответа:
```python
# Было:
return result.get("reply", None)

# Стало:
return result.get("response_text", None)
```

**Проблема 2**: Backend отправлял `issue_type.value` (например, `"auto_resolvable"`), а ML сервис ожидает русские строки (`"Типовой"`, `"Простой"`, `"Сложный"`)

**Решение**: Добавлен маппинг:
```python
problem_type_map = {
    IssueType.AUTO_RESOLVABLE: "Типовой",
    IssueType.SIMPLE: "Простой",
    IssueType.COMPLEX: "Сложный"
}
payload["problem_type"] = problem_type_map.get(issue_type, "Сложный")
```

## Как использовать

### Запуск ML сервиса
```bash
cd ml
python app.py
# или
./start_ml_service.sh
```

Сервис будет доступен на `http://localhost:8000`

### Запуск Backend
```bash
cd backend
python run.py
```

Backend будет доступен на `http://localhost:8002`

### Переменные окружения
Убедитесь, что установлена переменная:
```bash
export ML_SERVICE_URL=http://localhost:8000
```

Или создайте `.env` файл в `backend/`:
```
ML_SERVICE_URL=http://localhost:8000
```

## Тестирование

### 1. Проверка ML сервиса
```bash
curl http://localhost:8000/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "auto_reply_available": true
}
```

### 2. Тест классификации
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Не могу войти в систему, забыл пароль",
    "subject": "Проблема с входом"
  }'
```

### 3. Тест автоответа
```bash
curl -X POST http://localhost:8000/auto_reply \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Как сбросить пароль?",
    "problem_type": "Типовой",
    "category": "Общие вопросы"
  }'
```

### 4. Тест полной интеграции через Backend
```bash
curl -X POST http://localhost:8002/tickets/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "source": "portal",
    "subject": "Проблема с паролем",
    "body": "Не могу войти в систему, забыл пароль",
    "language": "ru"
  }'
```

## Важные замечания

1. **Используется `app.py`**, а не `api.py`
   - `app.py` - современная версия с правильными форматами
   - `api.py` - старая версия (можно удалить или оставить для совместимости)

2. **Порты**:
   - ML сервис: `8000`
   - Backend: `8002`
   - Убедитесь, что порты свободны

3. **Модели должны быть обучены**:
   - `models/classifier_category.pkl`
   - `models/classifier_priority.pkl`
   - `models/classifier_problem_type.pkl`
   - `models/sentence_transformer_model/` (опционально)

4. **Файл `responses.json`** должен существовать для работы автоответа

## Обработка ошибок

Backend имеет fallback значения на случай недоступности ML сервиса:
- Категория: "Общие вопросы"
- Приоритет: MEDIUM
- Тип проблемы: COMPLEX
- Уверенность: 0.3

Это позволяет системе работать даже при недоступности ML сервиса, хотя и с ограниченной функциональностью.

