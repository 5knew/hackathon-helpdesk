# API Connection Guide

## Конфигурация

Frontend и Backend связаны через REST API.

### Базовый URL
- **Backend API**: `http://localhost:8002` (по умолчанию)
- **ML Service**: `http://localhost:8000` (используется backend'ом)

### Переменные окружения
Создайте файл `.env` в папке `frontend/`:
```
VITE_API_URL=http://localhost:8002
VITE_ML_SERVICE_URL=http://localhost:8000
```

## Основные эндпоинты

### Тикеты
- `POST /submit_ticket` - Создание нового тикета
- `GET /tickets` - Список тикетов (с фильтрацией)
- `GET /tickets/{id}` - Детали тикета
- `PUT /tickets/{id}` - Обновление тикета
- `GET /tickets/search?q=query` - Поиск тикетов
- `GET /tickets/overdue` - Просроченные тикеты

### Комментарии
- `GET /tickets/{id}/comments` - Получить комментарии
- `POST /tickets/{id}/comments` - Добавить комментарий

### Feedback (CSAT)
- `POST /tickets/{id}/feedback` - Отправить оценку

### Шаблоны
- `GET /templates` - Получить шаблоны
- `POST /templates` - Создать шаблон

### Метрики и аналитика
- `GET /metrics` - Получить метрики дашборда
- `GET /analytics/performance` - Аналитика производительности
- `GET /export/metrics` - Экспорт метрик (CSV/JSON)

## Использование в коде

### Единая функция API запросов
Все API вызовы используют `apiRequest` из `utils/apiConfig.ts`:

```typescript
import { apiRequest } from './utils/apiConfig';

const tickets = await apiRequest<Ticket[]>('/tickets?user_id=user@example.com');
```

### Готовые функции
Используйте готовые функции из `utils/ticket.ts`:

```typescript
import { getTickets, getTicket, addComment } from './utils/ticket';

// Получить тикеты
const response = await getTickets('user@example.com', 'Pending', undefined, undefined, 50, 0);

// Получить тикет
const ticket = await getTicket(123);

// Добавить комментарий
const comment = await addComment(123, 'Текст комментария', false);
```

## CORS

Backend настроен для приема запросов с любого origin (для разработки).
В production измените в `backend/main.py`:
```python
allow_origins=["http://your-frontend-domain.com"]
```

## Обработка ошибок

Все функции API автоматически обрабатывают ошибки и выбрасывают исключения с понятными сообщениями.

Пример:
```typescript
try {
  const ticket = await getTicket(123);
} catch (error) {
  console.error('Ошибка:', error.message);
  showToast('Не удалось загрузить тикет', 'error');
}
```


