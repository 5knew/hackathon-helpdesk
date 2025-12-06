# Настройка базы данных PostgreSQL

## Проблема
Автоматическое создание базы данных не работает из-за проблем с кодировкой и аутентификацией.

## Решение

### Вариант 1: Использовать pgAdmin (рекомендуется)

1. Откройте **pgAdmin 4** (должен быть установлен с PostgreSQL)
2. Подключитесь к серверу PostgreSQL (localhost)
3. Правой кнопкой на **Databases** → **Create** → **Database**
4. Имя базы данных: `helpdesk_db`
5. Нажмите **Save**

### Вариант 2: Использовать psql через командную строку

Откройте командную строку и выполните:

```bash
"C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres
```

Затем в psql выполните:
```sql
CREATE DATABASE helpdesk_db;
\q
```

### Вариант 3: Использовать SQL команду напрямую

Если вы знаете пароль PostgreSQL, выполните:

```powershell
$env:PGPASSWORD="ваш_пароль"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE helpdesk_db;"
```

## После создания базы данных

Запустите скрипт инициализации таблиц:

```bash
cd backend
python setup_db.py
```

Или только создание таблиц (если база уже существует):

```bash
cd backend
python -c "from setup_db import init_tables, seed_data; init_tables(); seed_data()"
```

## Проверка

После создания базы данных и таблиц, проверьте подключение:

```bash
python -c "from database import engine; from sqlalchemy import text; conn = engine.connect(); print('Connected!'); conn.close()"
```



