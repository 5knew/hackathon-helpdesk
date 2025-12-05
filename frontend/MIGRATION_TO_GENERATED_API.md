# Миграция на сгенерированные API

## Что было сделано

Все функции, которые используют эндпоинты из нового OpenAPI API, были обновлены для использования сгенерированных методов из `apiGenerated.ts`.

## Обновленные функции

### ✅ Используют новый API (`api.tickets.*`)

1. **`getUserTickets()`** в `src/utils/api.ts`
   - Теперь использует `api.tickets.list()`
   - Добавлена обратная совместимость с преобразованием типов

2. **`getTicketById()`** в `src/utils/api.ts`
   - Теперь использует `api.tickets.getById()`
   - Добавлена обратная совместимость с преобразованием типов

3. **`updateTicketStatus()`** в `src/utils/api.ts`
   - Теперь использует `api.tickets.update()`
   - Добавлена обратная совместимость с преобразованием типов

4. **`submitTicketToAPI()`** в `src/utils/ticket.ts`
   - Теперь использует `api.tickets.create()`
   - Обновлена логика обработки ответа

5. **`getTicket()`** в `src/utils/ticket.ts`
   - Теперь использует `api.tickets.getById()`
   - Добавлена обратная совместимость с преобразованием типов

6. **`updateTicket()`** в `src/utils/ticket.ts`
   - Теперь использует `api.tickets.update()`
   - Добавлена обратная совместимость с преобразованием типов

7. **`Dashboard.tsx`** и **`Analytics.tsx`**
   - Используют `api.tickets.list()` вместо `getUserTickets()`

## Функции, которые остались на старом API

Эти функции остались на старом API, так как соответствующие эндпоинты пока не реализованы в новом OpenAPI:

- **`getTicketComments()`** - `/tickets/{id}/comments` не реализован
- **`getTicketHistory()`** - `/tickets/{id}/history` не реализован
- **`getTemplates()`** - `/templates` не реализован
- **`getIntegrations()`** - `/integrations` не реализован
- **`fetchMetrics()`** - `/metrics` не реализован

Все эти функции помечены комментариями `ВНИМАНИЕ` с указанием причины.

## Преобразование типов

Поскольку новый API использует UUID для ID (строки), а старый код ожидает числа, добавлены преобразования:

```typescript
// Новый тип (TicketResponse)
{
  id: string, // UUID
  user_id: string, // UUID
  body: string,
  status: 'new' | 'auto_resolved' | 'in_work' | 'waiting' | 'closed',
  // ...
}

// Старый тип (Ticket)
{
  id: number,
  user_id: string,
  problem_description: string,
  status: string,
  // ...
}
```

Все функции автоматически преобразуют новые типы в старые для обратной совместимости.

## Статусы тикетов

Старые статусы (`'Open'`, `'In Progress'`, `'Pending'`, `'Closed'`) преобразуются в новые:
- `'Open'` → `'new'`
- `'In Progress'` → `'in_work'`
- `'Pending'` → `'waiting'`
- `'Closed'` → `'closed'`

## Рекомендации

1. **Для новых функций** используйте напрямую `api.tickets.*`, `api.auth.*` из `apiGenerated.ts`
2. **Для существующего кода** старые функции работают через обёртки, но рекомендуется постепенно мигрировать
3. **При добавлении новых эндпоинтов** в backend:
   - Регенерируйте типы: `npm run generate:api`
   - Добавьте методы в `apiGenerated.ts`
   - Обновите старые функции для использования новых методов

## Примеры использования

### Новый способ (рекомендуется)

```typescript
import { api } from './utils/apiGenerated';

// Получить список тикетов
const tickets = await api.tickets.list({ status: 'in_work' });

// Создать тикет
const newTicket = await api.tickets.create({
  source: 'portal',
  user_id: userId,
  body: 'Описание проблемы',
  language: 'ru'
});

// Обновить тикет
const updated = await api.tickets.update(ticketId, {
  status: 'closed'
});
```

### Старый способ (работает через обёртки)

```typescript
import { getUserTickets, getTicketById } from './utils/api';

// Эти функции теперь используют новый API внутри
const tickets = await getUserTickets({ status: ['In Progress'] });
const ticket = await getTicketById(123);
```

