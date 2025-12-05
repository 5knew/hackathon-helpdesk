# Инструкция по запуску полной системы

## Архитектура

```
Frontend (React) :3000  →  Backend (FastAPI) :8001  →  ML Service (FastAPI) :8000
```

## Порты

- **Frontend**: `http://localhost:3000`
- **Backend (Core API)**: `http://localhost:8002`
- **ML Service**: `http://localhost:8000`

## Запуск системы

### 1. Запуск ML Service

```bash
cd ml
python3 api.py
# или
python3 app.py
```

ML сервис будет доступен на `http://localhost:8000`

### 2. Запуск Backend (Core API)

```bash
cd backend
pip install -r requirements.txt
python3 run.py
```

Backend будет доступен на `http://localhost:8001`

### 3. Запуск Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:3000`

## Проверка работы

1. Откройте `http://localhost:3000` в браузере
2. Войдите или зарегистрируйтесь
3. Отправьте тестовую заявку
4. Проверьте метрики на дашборде

## API Endpoints

### Backend (Core API)

- `POST /submit_ticket` - Отправка новой заявки
- `GET /metrics` - Получение метрик для дашборда
- `GET /docs` - Swagger документация

### ML Service

- `POST /predict` - Классификация тикета
- `POST /auto_reply` - Генерация автоответа
- `GET /health` - Проверка здоровья сервиса
- `GET /docs` - Swagger документация

## Переменные окружения

### Backend

```bash
export ML_SERVICE_URL="http://localhost:8000"  # URL ML сервиса
```

### Frontend

Создайте файл `.env` в папке `frontend`:

```
VITE_API_URL=http://localhost:8002
```

## Устранение проблем

1. **CORS ошибки**: Убедитесь, что backend запущен и CORS настроен правильно
2. **ML сервис не отвечает**: Проверьте, что ML сервис запущен на порту 8000
3. **Метрики не загружаются**: Проверьте подключение к базе данных SQLite

