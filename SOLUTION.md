# Решение проблемы "Failed to fetch"

## Проблема
Фронтенд показывает ошибку "Failed to fetch" при попытке регистрации или входа. Это происходит потому, что бэкенд не может подключиться к базе данных PostgreSQL.

## Причина
База данных `helpdesk_db` не создана в PostgreSQL, или есть проблемы с подключением.

## Решение (выберите один вариант)

### ✅ Вариант 1: Создать базу данных через pgAdmin (РЕКОМЕНДУЕТСЯ)

1. **Откройте pgAdmin 4**
   - Найдите в меню Пуск "pgAdmin 4"
   - Или откройте браузер и перейдите на `http://localhost/pgadmin4`

2. **Подключитесь к серверу PostgreSQL**
   - При первом запуске может потребоваться пароль, который вы установили при установке PostgreSQL
   - Если не помните пароль, попробуйте стандартные: `postgres`, `admin`, или тот, который вы устанавливали

3. **Создайте базу данных**
   - Правой кнопкой на **Databases** → **Create** → **Database**
   - В поле **Database**: введите `helpdesk_db`
   - Нажмите **Save**

4. **Создайте таблицы**
   ```powershell
   cd C:\Users\Anubis\Desktop\hackathon-helpdesk\backend
   python -c "import os; os.environ['USE_SQLITE'] = 'false'; from database import Base, engine; from models.ticket import Ticket; from models.user import User; from models.department import Department; from models.operator import Operator; from models.category import Category; from models.ml_model import MLModel; from models.ai_prediction import AIPrediction; from models.ai_auto_response import AIAutoResponse; from models.ticket_message import TicketMessage; from models.daily_stat import DailyStat; from models.training_sample import TrainingSample; Base.metadata.create_all(bind=engine); print('Tables created!')"
   ```

5. **Перезапустите бэкенд**
   - Остановите текущий процесс бэкенда (если запущен)
   - Запустите заново: `python run.py`

### ✅ Вариант 2: Использовать командную строку

Если у вас есть доступ к psql и вы знаете пароль PostgreSQL:

```powershell
# Установите пароль (замените на ваш пароль)
$env:PGPASSWORD="admin"

# Создайте базу данных
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -U postgres -c "CREATE DATABASE helpdesk_db;"
```

Затем выполните шаги 4-5 из Варианта 1.

## Проверка

После создания базы данных и таблиц:

1. **Проверьте бэкенд**: http://localhost:8002/health должен вернуть `{"status":"healthy"}`

2. **Попробуйте зарегистрироваться** на фронтенде

3. **Попробуйте войти** в систему

Если все работает - проблема решена! ✅

## Если проблема сохраняется

1. Проверьте, что PostgreSQL запущен:
   ```powershell
   Get-Service -Name "*postgresql*"
   ```

2. Проверьте, что бэкенд запущен на порту 8002:
   ```powershell
   netstat -ano | findstr ":8002"
   ```

3. Проверьте логи бэкенда на наличие ошибок подключения к БД

## Дополнительная информация

- База данных должна называться: `helpdesk_db`
- Пользователь по умолчанию: `postgres`
- Пароль: тот, который вы установили при установке PostgreSQL
- Хост: `localhost`
- Порт: `5432`

Если вы не помните пароль PostgreSQL, вы можете:
1. Переустановить PostgreSQL с новым паролем
2. Или сбросить пароль через pgAdmin (требуются права администратора)



