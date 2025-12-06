"""
Новый main.py с использованием новой архитектуры БД
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import tickets, auth, comments, notifications, feedback, templates, ticket_history

app = FastAPI(
    title="Help Desk API",
    description="AI-powered Help Desk system with PostgreSQL",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить до конкретных доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
# ВАЖНО: Роутер комментариев должен быть ПЕРЕД роутером тикетов,
# чтобы более специфичные маршруты обрабатывались первыми
app.include_router(auth.router)
app.include_router(comments.router)  # Комментарии ПЕРЕД тикетами
app.include_router(notifications.router)  # Уведомления
app.include_router(feedback.router)  # CSAT Feedback
app.include_router(templates.router)  # Шаблоны ответов
app.include_router(ticket_history.router)  # История изменений
app.include_router(tickets.router)


@app.get("/")
def read_root():
    return {
        "message": "Help Desk Core API is running",
        "version": "2.0.0",
        "database": "PostgreSQL",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

