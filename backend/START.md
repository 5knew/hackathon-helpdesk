# 🚀 Инструкция по запуску

## ✅ Что уже сделано:

1. ✅ Старый `main.py` переименован в `main_old_backup.py`
2. ✅ Новый `main.py` с PostgreSQL архитектурой готов
3. ✅ База данных `helpdesk_db` инициализирована
4. ✅ Все таблицы созданы
5. ✅ Начальные данные добавлены (департаменты, категории, ML модель)

## 🚀 Запуск приложения:

### Вариант 1: Использовать run.py
```bash
cd /Users/s.muratkhan/Desktop/hackathon-helpdesk/backend
python3 run.py
```

### Вариант 2: Прямой запуск через uvicorn
```bash
cd /Users/s.muratkhan/Desktop/hackathon-helpdesk/backend
uvicorn main:app --host 0.0.0.0 --port 8002
```

## 📝 Проверка работы:

1. **Health check:**
   ```bash
   curl http://localhost:8002/health
   ```

2. **Документация API:**
   Откройте в браузере: http://localhost:8002/docs

3. **Создание тикета:**
   ```bash
   curl -X POST "http://localhost:8002/tickets/create" \
     -H "Content-Type: application/json" \
     -d '{
       "source": "email",
       "user_id": "550e8400-e29b-41d4-a716-446655440000",
       "subject": "Тест",
       "body": "Проблема с доступом",
       "language": "ru"
     }'
   ```

## ⚙️ Настройки:

База данных настроена на:
- **Host:** localhost
- **Port:** 5432
- **Database:** helpdesk_db
- **User:** postgres
- **Password:** postgres

Если нужно изменить, создайте файл `.env`:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/helpdesk_db
ML_SERVICE_URL=http://localhost:8000
```

## 📊 Доступные эндпоинты:

- `GET /` - Главная страница
- `GET /health` - Health check
- `POST /tickets/create` - Создание тикета
- `GET /tickets/{ticket_id}` - Получение тикета
- `GET /tickets` - Список тикетов
- `PUT /tickets/{ticket_id}` - Обновление тикета

## 🔍 Проверка БД:

```bash
psql -U postgres -d helpdesk_db -c "\dt"
```

## ⚠️ Важно:

- Старый `main.py` сохранен как `main_old_backup.py` (можно удалить после проверки)
- Все данные теперь в PostgreSQL, не в SQLite
- ID теперь UUID, а не INTEGER

