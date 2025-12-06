# Быстрое исправление - Вход в систему

## ✅ Пользователи восстановлены!

Пароли обновлены:
- **admin@helpdesk.com** / `admin123` ✅
- **ibragim@gmail.com** / `admin!` ✅

## Запуск бэкенда

Бэкенд запущен в фоновом режиме. Если ошибка `ERR_CONNECTION_REFUSED` все еще есть:

### Вариант 1: Через терминал
```powershell
cd backend
python main.py
```

### Вариант 2: Через uvicorn (рекомендуется)
```powershell
cd backend
uvicorn main:app --reload --port 8002
```

## Проверка

1. Откройте http://localhost:8002/docs
   - Должна открыться документация API
   - Должен быть виден эндпоинт `POST /auth/login`

2. Попробуйте войти:
   - Email: `admin@helpdesk.com`
   - Password: `admin123`

   Или:
   - Email: `ibragim@gmail.com`
   - Password: `admin!`

## Если бэкенд не запускается

Проверьте логи в терминале на наличие ошибок. Возможные проблемы:
- База данных не подключена
- Порт 8002 занят другим процессом
- Ошибки импорта модулей

## Остановка процессов на порту 8002

Если порт занят:
```powershell
# Найти процесс
netstat -ano | findstr :8002

# Остановить (замените PID)
taskkill /F /PID <PID>
```

