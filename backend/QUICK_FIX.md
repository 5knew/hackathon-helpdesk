# Быстрое решение проблемы "Failed to fetch"

## Проблема
Фронтенд не может подключиться к бэкенду из-за отсутствия базы данных PostgreSQL.

## Решение (3 шага)

### Шаг 1: Создайте базу данных вручную

**Вариант A: Через pgAdmin (самый простой)**
1. Откройте **pgAdmin 4** (ищите в меню Пуск)
2. Подключитесь к серверу PostgreSQL (может потребоваться пароль, который вы установили при установке)
3. Правой кнопкой на **Databases** → **Create** → **Database**
4. Имя: `helpdesk_db`
5. Нажмите **Save**

**Вариант B: Через командную строку**
```powershell
# Найдите путь к psql (обычно здесь):
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres

# В psql выполните:
CREATE DATABASE helpdesk_db;
\q
```

### Шаг 2: Создайте таблицы

После создания базы данных, выполните:

```powershell
cd C:\Users\Anubis\Desktop\hackathon-helpdesk\backend
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine); print('Tables created!')"
```

### Шаг 3: Перезапустите бэкенд

Остановите текущий бэкенд (если запущен) и запустите заново:

```powershell
cd C:\Users\Anubis\Desktop\hackathon-helpdesk\backend
python run.py
```

## Проверка

После этого попробуйте:
1. Зарегистрироваться на фронтенде
2. Войти в систему

Если все работает, проблема решена! ✅

## Альтернатива: Использовать SQLite временно

Если PostgreSQL не работает, можно временно использовать SQLite:

1. Измените `backend/database.py`:
```python
DATABASE_URL = "sqlite:///./helpdesk.db"
```

2. Запустите бэкенд - таблицы создадутся автоматически

Но рекомендуется использовать PostgreSQL для продакшена.



