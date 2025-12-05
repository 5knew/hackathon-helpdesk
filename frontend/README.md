# AI AutoResponder - Frontend

React + TypeScript + Vite проект для единого входа и мониторинга.

## Технологии

- **React 19** - UI библиотека
- **TypeScript** - типизация
- **Vite** - сборщик и dev-сервер
- **CSS** - стилизация

## Установка

```bash
npm install
```

## Запуск dev-сервера

```bash
npm run dev
```

Приложение откроется на `http://localhost:3000`

## Сборка для production

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Предпросмотр production сборки

```bash
npm run preview
```

## Структура проекта

```
frontend/
├── src/
│   ├── App.tsx          # Главный компонент
│   ├── App.css          # Стили компонента App
│   ├── main.tsx         # Точка входа
│   ├── index.css        # Глобальные стили
│   └── vite-env.d.ts    # Типы Vite
├── index.html           # HTML шаблон
├── vite.config.ts       # Конфигурация Vite
├── tsconfig.json        # Конфигурация TypeScript
└── package.json         # Зависимости и скрипты
```

## Разработка

Старые HTML/CSS/JS файлы сохранены в корне проекта и не используются React приложением.

