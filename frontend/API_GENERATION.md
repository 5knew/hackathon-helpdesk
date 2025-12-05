# Генерация API и моделей из OpenAPI спецификации

Этот проект использует автоматическую генерацию TypeScript типов и API клиента из OpenAPI спецификации backend.

## Установка

Инструменты для генерации уже установлены в `devDependencies`:
- `openapi-typescript` - генерация TypeScript типов из OpenAPI спецификации

## Регенерация типов

После изменения API в backend, необходимо регенерировать типы:

```bash
npm run generate:api
```

Этот скрипт:
1. Получает OpenAPI спецификацию с `http://localhost:8002/openapi.json`
2. Генерирует TypeScript типы в `src/types/api.ts`

**Важно:** Убедитесь, что backend запущен на порту 8002 перед регенерацией типов.

## Структура файлов

### `src/types/api.ts`
Автоматически сгенерированный файл с типами из OpenAPI спецификации. **Не редактируйте этот файл вручную!**

### `src/utils/apiClient.ts`
Базовый API клиент с типизацией. Предоставляет методы:
- `get<T>(path, options?)` - GET запрос
- `post<T>(path, options?)` - POST запрос
- `put<T>(path, options?)` - PUT запрос
- `delete<T>(path, options?)` - DELETE запрос

### `src/utils/apiGenerated.ts`
Удобные обёртки для работы с API, сгруппированные по функциональности:
- `api.auth` - аутентификация
- `api.tickets` - работа с тикетами
- `api.health` - проверка здоровья API

## Использование

### Пример 1: Использование готовых API методов

```typescript
import { api } from './utils/apiGenerated';
import { storage } from './utils/storage';

// Регистрация
const user = await api.auth.register({
  email: 'user@example.com',
  password: 'password123',
  name: 'John Doe'
});

// Вход
const tokenResponse = await api.auth.login({
  email: 'user@example.com',
  password: 'password123'
});

// Сохранить токен
storage.saveUser(
  tokenResponse.email,
  '', // пароль не нужен после входа
  tokenResponse.access_token,
  tokenResponse.user_id,
  tokenResponse.name,
  tokenResponse.role
);

// Получить список тикетов
const tickets = await api.tickets.list({
  skip: 0,
  limit: 10,
  status: 'in_work'
});

// Создать тикет
const newTicket = await api.tickets.create({
  source: 'portal',
  user_id: tokenResponse.user_id,
  subject: 'Проблема с доступом',
  body: 'Не могу войти в систему',
  language: 'ru'
});
```

### Пример 2: Использование базового API клиента

```typescript
import { apiClient } from './utils/apiClient';
import type { TicketResponse, TicketCreate } from './utils/apiClient';

// Прямое использование клиента
const ticket: TicketResponse = await apiClient.post<TicketResponse>('/tickets/create', {
  body: {
    source: 'portal',
    user_id: 'user-uuid',
    body: 'Описание проблемы',
    language: 'ru'
  }
});

// GET запрос с параметрами
const tickets: TicketResponse[] = await apiClient.get<TicketResponse[]>('/tickets', {
  query: {
    skip: 0,
    limit: 50,
    status: 'in_work'
  }
});

// PUT запрос с path параметрами
const updated: TicketResponse = await apiClient.put<TicketResponse>('/tickets/{ticket_id}', {
  params: {
    ticket_id: 'ticket-uuid'
  },
  body: {
    status: 'closed'
  }
});
```

### Пример 3: Использование типов из OpenAPI

```typescript
import type {
  TicketResponse,
  TicketCreate,
  TicketUpdate,
  UserResponse,
  TokenResponse,
  TicketStatus,
  TicketPriority,
  TicketSource
} from './utils/apiClient';

// Типы можно использовать для аннотации переменных
const status: TicketStatus = 'in_work';
const priority: TicketPriority = 'high';
const source: TicketSource = 'portal';

// Или для типизации функций
function processTicket(ticket: TicketResponse): void {
  console.log(`Ticket ${ticket.id} has status ${ticket.status}`);
}
```

## Авторизация

API клиент автоматически добавляет токен авторизации из `localStorage` в заголовок `Authorization: Bearer <token>`.

Токен сохраняется через `storage.saveUser()` после успешного входа.

## Обработка ошибок

Все методы API клиента выбрасывают исключения при ошибках HTTP запросов:

```typescript
try {
  const ticket = await api.tickets.getById('invalid-id');
} catch (error) {
  if (error instanceof Error) {
    console.error('Ошибка API:', error.message);
  }
}
```

## Интеграция с существующим кодом

Старые функции в `src/utils/api.ts` можно постепенно заменить на новые методы из `apiGenerated.ts`:

```typescript
// Старый способ
import { getUserTickets } from './utils/api';

// Новый способ
import { api } from './utils/apiGenerated';
const tickets = await api.tickets.list();
```

## Обновление после изменений в backend

1. Убедитесь, что backend запущен
2. Выполните `npm run generate:api`
3. Проверьте, что новые типы корректны
4. Обновите `apiGenerated.ts` при необходимости (если добавились новые эндпоинты)

