# Анализ интеграции Backend и ML сервиса

## Текущее состояние

### Архитектура
- **Backend**: FastAPI на порту 8002 (`backend/run.py`)
- **ML Service**: FastAPI на порту 8000 (должен быть запущен отдельно)
- **Связь**: Backend вызывает ML сервис через HTTP запросы

### Сервисы Backend, использующие ML
1. **AIClassifier** (`backend/services/ai_classifier.py`)
   - Вызывает `/predict` для классификации тикетов
   - Использует переменную окружения `ML_SERVICE_URL` (по умолчанию `http://localhost:8000`)

2. **AutoResolver** (`backend/services/auto_resolver.py`)
   - Вызывает `/auto_reply` для автоматических ответов
   - Использует переменную окружения `ML_SERVICE_URL`

## Обнаруженные проблемы

### 1. Два файла ML сервиса с разными форматами

#### `ml/api.py` (старая версия)
- Использует модель `AutoReplyResponse` с полем `reply`
- Формат запроса `/predict`: `{"subject": str, "body": str}`
- Формат ответа `/auto_reply`: `{"reply": str, "can_auto_reply": bool, ...}`

#### `ml/app.py` (новая версия)
- Использует модель `AutoReplyResponse` с полем `response_text`
- Формат запроса `/predict`: `{"text": str, "subject": Optional[str]}`
- Формат ответа `/auto_reply`: `{"response_text": str, "can_auto_reply": bool, ...}`

**Проблема**: Backend ожидает `reply`, но `app.py` возвращает `response_text`

### 2. Несоответствие форматов данных

#### Приоритеты
- **ML возвращает**: "Низкий", "Средний", "Высокий", "Критический" (русские строки)
- **Backend ожидает**: `TicketPriority` enum: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- **Решение**: Маппинг в `AIClassifier._map_priority()` ✅ (работает)

#### Типы проблем
- **ML возвращает**: "Типовой", "Простой", "Сложный" (русские строки)
- **Backend ожидает**: `IssueType` enum: `AUTO_RESOLVABLE`, `SIMPLE`, `COMPLEX`
- **Решение**: Маппинг в `AIClassifier._map_issue_type()` ✅ (работает)

#### Автоответ
- **ML (app.py) возвращает**: `{"response_text": str, "can_auto_reply": bool, ...}`
- **Backend ожидает**: `{"reply": str, "can_auto_reply": bool, ...}`
- **Проблема**: Backend не может получить текст ответа ❌

### 3. Проблема с problem_type в auto_reply

В `auto_resolver.py` строка 42:
```python
payload["problem_type"] = issue_type.value
```

Но `issue_type.value` возвращает `"auto_resolvable"`, а ML сервис ожидает `"Типовой"`.

### 4. Несоответствие формата запроса /predict

- **Backend отправляет**: `{"subject": str, "body": str}` ✅
- **ML (api.py) ожидает**: `{"subject": str, "body": str}` ✅
- **ML (app.py) ожидает**: `{"text": str, "subject": Optional[str]}` ❌

## Рекомендации по исправлению

### Вариант 1: Использовать `app.py` (рекомендуется)
`app.py` более современный и имеет лучшую структуру.

**Необходимые изменения:**

1. **Исправить `backend/services/auto_resolver.py`**:
   ```python
   # Строка 54: изменить
   return result.get("reply", None)
   # на
   return result.get("response_text", None)
   ```

2. **Исправить маппинг problem_type в `auto_resolver.py`**:
   ```python
   # Строка 42: изменить
   payload["problem_type"] = issue_type.value
   # на
   problem_type_map = {
       IssueType.AUTO_RESOLVABLE: "Типовой",
       IssueType.SIMPLE: "Простой",
       IssueType.COMPLEX: "Сложный"
   }
   payload["problem_type"] = problem_type_map.get(issue_type, "Сложный")
   ```

3. **Исправить формат запроса в `ai_classifier.py`**:
   ```python
   # Строка 37-40: изменить
   payload = {
       "subject": subject or "Заявка",
       "body": body
   }
   # на
   payload = {
       "text": body,
       "subject": subject or ""
   }
   ```

### Вариант 2: Использовать `api.py` (быстрое решение)
Меньше изменений, но менее современный код.

**Необходимые изменения:**

1. **Убедиться, что используется `api.py`** при запуске ML сервиса
2. **Исправить маппинг problem_type** (как в варианте 1)

### Вариант 3: Унифицировать оба файла
Создать единый интерфейс, поддерживающий оба формата.

## Проверка работоспособности

### Тест 1: Проверка доступности ML сервиса
```bash
curl http://localhost:8000/health
```

### Тест 2: Проверка классификации
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"subject": "Проблема с паролем", "body": "Не могу войти в систему"}'
```

### Тест 3: Проверка автоответа
```bash
curl -X POST http://localhost:8000/auto_reply \
  -H "Content-Type: application/json" \
  -d '{"text": "Как сбросить пароль?", "problem_type": "Типовой", "category": "Общие вопросы"}'
```

### Тест 4: Проверка интеграции через Backend
```bash
curl -X POST http://localhost:8002/tickets/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "source": "portal",
    "subject": "Проблема с паролем",
    "body": "Не могу войти в систему",
    "language": "ru"
  }'
```

## План действий

1. ✅ Определить, какой файл использовать (`app.py` или `api.py`)
2. ⏳ Исправить несоответствия в форматах данных
3. ⏳ Обновить документацию
4. ⏳ Протестировать интеграцию
5. ⏳ Добавить обработку ошибок и fallback значения

## Переменные окружения

Убедитесь, что установлена переменная окружения:
```bash
export ML_SERVICE_URL=http://localhost:8000
```

Или в `.env` файле:
```
ML_SERVICE_URL=http://localhost:8000
```

## Порты

- **Backend**: 8002
- **ML Service**: 8000

Убедитесь, что порты не конфликтуют и оба сервиса запущены.

