# Helpdesk Frontend - React + TypeScript

Frontend приложение для системы helpdesk, переписанное на React с TypeScript.

## Технологии

- **React 18** - UI библиотека
- **TypeScript** - типизация
- **React Router** - маршрутизация
- **Vite** - сборщик и dev-сервер

## Установка

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу `http://localhost:3000`

## Сборка для продакшена

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Предпросмотр продакшен сборки

```bash
npm run preview
```

## Структура проекта

```
frontend/
├── src/
│   ├── components/      # Переиспользуемые компоненты
│   │   ├── Badge.tsx
│   │   ├── BrandBar.tsx
│   │   └── Chip.tsx
│   ├── pages/           # Страницы приложения
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── types/           # TypeScript типы
│   │   └── index.ts
│   ├── utils/           # Утилиты
│   │   ├── metrics.ts
│   │   ├── storage.ts
│   │   ├── ticket.ts
│   │   └── toast.ts
│   ├── App.tsx          # Главный компонент с роутингом
│   ├── main.tsx         # Точка входа
│   └── index.css        # Глобальные стили
├── index.html           # HTML шаблон
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Функциональность

- **Авторизация** - вход и регистрация (данные хранятся в localStorage)
- **Дашборд** - отправка заявок и просмотр метрик
- **Защищенные маршруты** - автоматическое перенаправление на страницу входа
- **Метрики** - отображение статистики работы системы

## Миграция со старого кода

Старые HTML файлы (`index.html`, `register.html`, `dashboard.html`) и `app.js` сохранены в корне папки `frontend/` для справки, но больше не используются. Вся функциональность перенесена в React компоненты.

