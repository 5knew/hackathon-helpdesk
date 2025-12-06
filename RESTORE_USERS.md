# Восстановление пользователей

## ✅ Пользователи восстановлены!

Проверка показала, что пользователи существуют в базе данных:

- **admin@helpdesk.com** (Админ) - Role: admin
- **ibragim@gmail.com** (Ibragim) - Role: client

## Пароли

- **admin@helpdesk.com**: `admin123`
- **ibragim@gmail.com**: `password123` (или тот, который был установлен ранее)

## Если нужно восстановить пользователей заново

Запустите скрипт:
```powershell
cd backend
python restore_users.py
```

Или используйте существующий скрипт:
```powershell
cd backend
python check_and_fix_db.py
```

## Запуск бэкенда

Бэкенд должен быть запущен на порту 8002. Если он не запущен:

```powershell
cd backend
python main.py
```

Или:
```powershell
cd backend
uvicorn main:app --reload --port 8002
```

## Проверка

1. Откройте http://localhost:8002/docs
2. Попробуйте войти через фронтенд:
   - Email: `admin@helpdesk.com`
   - Password: `admin123`

