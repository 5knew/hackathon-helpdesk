# 📋 Полный список всех API эндпоинтов

**Версия:** 2.0.0  
**База данных:** PostgreSQL  
**Дата:** 2025-12-05

---

## 🎯 CRUD операции для тикетов

### 1. CREATE - Создание тикета
```
POST /tickets/create
Content-Type: application/json

{
  "source": "email" | "chat" | "portal" | "phone",
  "user_id": "uuid",
  "subject": "string (optional)",
  "body": "string (required)",
  "language": "ru" | "kk" | "en"
}
```

**Ответ:** `TicketResponse` (200)

**Особенности:**
- Автоматическое создание пользователя, если не существует
- AI классификация тикета
- Автоматическое создание категории, если не существует
- Маршрутизация по департаментам
- Попытка автоматического решения
- Сохранение предсказаний ИИ

---

### 2. READ - Получение тикета
```
GET /tickets/{ticket_id}
```

**Ответ:** `TicketResponse` (200) или 404

**Параметры:**
- `ticket_id` (UUID) - ID тикета

---

### 3. READ ALL - Список тикетов
```
GET /tickets?skip=0&limit=50&status=new
```

**Ответ:** `List[TicketResponse]` (200)

**Параметры:**
- `skip` (int, default: 0) - Пропустить N записей
- `limit` (int, default: 50) - Максимум записей
- `status` (TicketStatus, optional) - Фильтр по статусу

**Статусы:**
- `new` - Новый
- `auto_resolved` - Автоматически решен
- `in_work` - В работе
- `waiting` - Ожидание
- `closed` - Закрыт

---

### 4. UPDATE - Обновление тикета
```
PUT /tickets/{ticket_id}
Content-Type: application/json

{
  "status": "new" | "auto_resolved" | "in_work" | "waiting" | "closed",
  "priority": "low" | "medium" | "high" | "critical",
  "category_id": "uuid (optional)",
  "assigned_department_id": "uuid (optional)",
  "assigned_operator_id": "uuid (optional)"
}
```

**Ответ:** `TicketResponse` (200) или 404

**Особенности:**
- Автоматическое обновление `updated_at`
- Автоматическая установка `closed_at` при закрытии

---

### 5. DELETE - Удаление тикета
```
DELETE /tickets/{ticket_id}
```

**Ответ:** 
```json
{
  "message": "Ticket deleted successfully",
  "ticket_id": "uuid"
}
```

**Особенности:**
- Soft delete (помечает как закрытый)
- Устанавливает статус `closed`
- Устанавливает `closed_at`

---

## 🔍 Служебные эндпоинты

### Health Check
```
GET /health
```

**Ответ:**
```json
{
  "status": "healthy"
}
```

---

### Root Endpoint
```
GET /
```

**Ответ:**
```json
{
  "message": "Help Desk Core API is running",
  "version": "2.0.0",
  "database": "PostgreSQL",
  "docs": "/docs"
}
```

---

### API Документация

#### Swagger UI
```
GET /docs
```

#### ReDoc
```
GET /redoc
```

#### OpenAPI Schema
```
GET /openapi.json
```

---

## 📊 Схемы данных

### TicketCreate
```json
{
  "source": "email",
  "user_id": "uuid",
  "subject": "string (optional)",
  "body": "string",
  "language": "ru"
}
```

### TicketResponse
```json
{
  "id": "uuid",
  "source": "email",
  "user_id": "uuid",
  "subject": "string",
  "body": "string",
  "language": "ru",
  "category_id": "uuid",
  "priority": "high",
  "issue_type": "complex",
  "ai_confidence": 0.89,
  "assigned_department_id": "uuid | null",
  "assigned_operator_id": "uuid | null",
  "status": "new",
  "auto_resolved": false,
  "created_at": "2025-12-05T...",
  "updated_at": "2025-12-05T...",
  "closed_at": "null | datetime"
}
```

### TicketUpdate
```json
{
  "status": "in_work",
  "priority": "high",
  "category_id": "uuid",
  "assigned_department_id": "uuid",
  "assigned_operator_id": "uuid"
}
```

---

## 🎯 Статусы HTTP

| Код | Описание |
|-----|----------|
| 200 | Успешно |
| 201 | Создано (для CREATE) |
| 404 | Не найдено |
| 500 | Ошибка сервера |

---

## 📝 Примеры использования

### Создание тикета
```bash
curl -X POST "http://localhost:8002/tickets/create" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "email",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "subject": "Проблема с доступом",
    "body": "Не могу войти в систему",
    "language": "ru"
  }'
```

### Получение тикета
```bash
curl "http://localhost:8002/tickets/{ticket_id}"
```

### Список тикетов
```bash
curl "http://localhost:8002/tickets?skip=0&limit=10"
```

### Фильтрация по статусу
```bash
curl "http://localhost:8002/tickets?status=new"
```

### Обновление тикета
```bash
curl -X PUT "http://localhost:8002/tickets/{ticket_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_work",
    "priority": "high"
  }'
```

### Удаление тикета
```bash
curl -X DELETE "http://localhost:8002/tickets/{ticket_id}"
```

---

## ✅ Статус эндпоинтов

| Endpoint | Метод | Статус | Тестировано |
|----------|-------|--------|-------------|
| `/tickets/create` | POST | ✅ | ✅ |
| `/tickets/{id}` | GET | ✅ | ✅ |
| `/tickets` | GET | ✅ | ✅ |
| `/tickets/{id}` | PUT | ✅ | ✅ |
| `/tickets/{id}` | DELETE | ✅ | ✅ |
| `/health` | GET | ✅ | ✅ |
| `/` | GET | ✅ | ✅ |
| `/docs` | GET | ✅ | ✅ |

**Все эндпоинты работают!** 🎉

---

**Документация обновлена:** 2025-12-05  
**Версия API:** 2.0.0

