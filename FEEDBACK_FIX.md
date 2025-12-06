# Исправление ошибки 404 для Feedback API

## Проблема
Ошибка 404 при обращении к `/tickets/{ticket_id}/feedback`

## Решение

### 1. Исправлена синтаксическая ошибка
Исправлен неправильный отступ в `backend/routers/tickets.py` (строка 316)

### 2. Порядок роутеров
Роутер `feedback` должен быть зарегистрирован **ПЕРЕД** роутером `tickets`, чтобы более специфичные маршруты обрабатывались первыми.

В `backend/main.py` порядок правильный:
```python
app.include_router(feedback.router)  # ПЕРЕД tickets.router
app.include_router(tickets.router)
```

### 3. Перезапуск бэкенда
**ВАЖНО:** После добавления нового роутера нужно перезапустить бэкенд!

```bash
# Остановите текущий процесс бэкенда (Ctrl+C)
# Затем запустите снова:
cd backend
python main.py
# или
uvicorn main:app --reload --port 8002
```

### 4. Проверка
После перезапуска проверьте в браузере:
- `http://localhost:8002/docs` - должен быть виден эндпоинт `POST /tickets/{ticket_id}/feedback`

## Эндпоинты Feedback API

- `POST /tickets/{ticket_id}/feedback` - Отправить CSAT оценку
- `GET /tickets/{ticket_id}/feedback` - Получить CSAT оценку (если есть)

## Примечание
Если ошибка 404 все еще возникает после перезапуска, проверьте:
1. Что роутер feedback импортирован в main.py
2. Что таблица `feedback` создана в базе данных (миграция выполнена)
3. Логи бэкенда на наличие ошибок при запуске

