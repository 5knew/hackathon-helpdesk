from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import sqlite3
import requests
import os

app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Ticket(BaseModel):
    user_id: str  # Changed to str to accept emails or UUIDs from frontend
    problem_description: str
    subject: str = ""  # Optional subject
    language: str = "ru"  # Language: "ru" or "kz"

class TicketResponse(BaseModel):
    ticket_id: int
    status: str
    message: str
    queue: str

class MetricsResponse(BaseModel):
    total_tickets: int
    closed_tickets: int
    auto_closed_tickets: int
    tickets_by_classification: Dict[str, int]
    tickets_by_queue: Dict[str, int]
    tickets_by_problem_type: Dict[str, int]
    accuracy_metrics: Dict[str, float]
    auto_resolution_rate: float
    avg_response_time: float

# --- Database Setup ---
DB_NAME = "tickets.db"

def init_db():
    # Connect to the database inside the backend folder
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Added 'queue' column for routing logic
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            problem_description TEXT NOT NULL,
            priority TEXT NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL,
            ml_classification TEXT,
            queue TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db() # Initialize the database on startup

# --- ML Service Integration ---
# Use environment variable for flexibility (Docker support)
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

def classify_ticket_with_ml(problem_description: str, subject: str = ""):
    """Calls the ML service to classify the ticket automatically."""
    try:
        # ML service expects: {"subject": str, "body": str}
        payload = {
            "subject": subject or "Заявка",
            "body": problem_description
        }
        response = requests.post(f"{ML_SERVICE_URL}/predict", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return {
            "category": result.get("category", "Неизвестно"),
            "priority": result.get("priority", "Средний"),
            "problem_type": result.get("problem_type", "Сложный"),
            "confidence": result.get("confidence", {})
        }
    except requests.exceptions.RequestException as e:
        print(f"Error calling ML service: {e}")
        # Fallback values
        return {
            "category": "Общие вопросы",
            "priority": "Средний",
            "problem_type": "Сложный",
            "confidence": {}
        }

def get_auto_reply_from_ml(text: str, category: str = None, problem_type: str = None):
    """Gets an automated reply from the ML service using FAISS semantic search."""
    try:
        payload = {"text": text}
        if category:
            payload["category"] = category
        if problem_type:
            payload["problem_type"] = problem_type
        response = requests.post(f"{ML_SERVICE_URL}/auto_reply", json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        # Проверяем, может ли система ответить автоматически
        if result.get("can_auto_reply", True):
            return result.get("reply", "Спасибо за обращение. Ваш запрос принят в работу.")
        else:
            # Если не может ответить автоматически, возвращаем стандартный ответ
            return "Спасибо за обращение. Ваш запрос принят в работу. Наш специалист свяжется с вами в ближайшее время."
    except requests.exceptions.RequestException as e:
        print(f"Error calling ML service for auto-reply: {e}")
        return "Спасибо за обращение. Ваш запрос принят в работу. Мы свяжемся с вами в ближайшее время."


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Helpdesk Core API is running. Go to /docs for documentation."}

@app.post("/submit_ticket", response_model=TicketResponse)
def submit_ticket(ticket: Ticket):
    """
    Receives a new ticket, automatically classifies it with ML, and decides on routing.
    Полностью автоматическая обработка без участия первой линии поддержки.
    """
    try:
        db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
        
        # 1. Automatic ML Classification (ИИ определяет категорию, приоритет и тип проблемы)
        ml_result = classify_ticket_with_ml(ticket.problem_description, ticket.subject)
        category = ml_result["category"]
        priority = ml_result["priority"]
        problem_type = ml_result["problem_type"]
        confidence = ml_result.get("confidence", {})

        # 2. Routing Logic согласно ТЗ
        status = "Pending"
        message = "Заявка принята в обработку."
        queue = "General"

        # A. Проверка типа проблемы (Типовой = автоматическое решение)
        if problem_type == "Типовой":
            # Автоматическое решение типовых инцидентов (~50% заявок)
            auto_reply = get_auto_reply_from_ml(ticket.problem_description, category, problem_type)
            if auto_reply:
                status = "Closed"
                queue = "Automated"
                message = auto_reply + f" (Автоматически закрыто. Категория: {category})"
            else:
                # Если не можем ответить автоматически, отправляем в общую очередь
                status = "Pending"
                queue = "GeneralSupport"
                message = f"Заявка принята в обработку. Категория: {category}"
        
        else:
            # B. Маршрутизация сложных кейсов в профильные департаменты
            # Эскалация по приоритету
            if priority == "Высокий":
                queue = "HighPriority"
                message = f"Заявка эскалирована в отдел высокого приоритета. Категория: {category}"
            # Маршрутизация по категории
            elif "Биллинг" in category or "платеж" in category.lower():
                queue = "Billing"
                message = f"Заявка направлена в отдел биллинга. Приоритет: {priority}"
            elif "Техническая" in category or "IT" in category:
                queue = "TechSupport"
                message = f"Заявка направлена в техническую поддержку. Приоритет: {priority}"
            elif "HR" in category or "кадр" in category.lower():
                queue = "HR"
                message = f"Заявка направлена в HR отдел. Приоритет: {priority}"
            elif "Клиентский" in category or "сервис" in category.lower():
                queue = "CustomerService"
                message = f"Заявка направлена в клиентский сервис. Приоритет: {priority}"
            else:
                queue = "GeneralSupport"
                message = f"Заявка направлена в общую поддержку. Категория: {category}, Приоритет: {priority}"

        # 3. Save to Database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Обновляем структуру БД для хранения всех данных ML классификации
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                problem_description TEXT NOT NULL,
                priority TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                ml_classification TEXT,
                problem_type TEXT,
                queue TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Добавляем новые колонки, если их нет (миграция)
        try:
            cursor.execute("ALTER TABLE tickets ADD COLUMN problem_type TEXT")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        try:
            cursor.execute("ALTER TABLE tickets ADD COLUMN confidence REAL")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        # Получаем значение уверенности
        confidence_value = confidence.get("problem_type", 0.0) if isinstance(confidence, dict) else 0.0
        
        cursor.execute(
            """INSERT INTO tickets 
               (user_id, problem_description, priority, category, status, ml_classification, problem_type, queue, confidence) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticket.user_id, ticket.problem_description, priority, category, status, 
             f"{category}|{priority}|{problem_type}", problem_type, queue, 
             confidence_value)
        )
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return TicketResponse(ticket_id=ticket_id, status=status, message=message, queue=queue)
    except Exception as e:
        import traceback
        print(f"Error in submit_ticket: {e}")
        print(traceback.format_exc())
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """
    Provides comprehensive metrics for the monitoring dashboard.
    Метрики для веб-панели мониторинга согласно ТЗ.
    """
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Базовые метрики
        total_tickets = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        closed_tickets = cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'Closed'").fetchone()[0]
        auto_closed = cursor.execute("SELECT COUNT(*) FROM tickets WHERE queue = 'Automated'").fetchone()[0]
        
        # Метрики по классификации
        classifications = cursor.execute(
            "SELECT category, COUNT(*) as count FROM tickets GROUP BY category"
        ).fetchall()
        
        # Метрики по очередям
        queues = cursor.execute(
            "SELECT queue, COUNT(*) as count FROM tickets GROUP BY queue"
        ).fetchall()
        
        # Метрики по типам проблем
        problem_types = cursor.execute(
            "SELECT problem_type, COUNT(*) as count FROM tickets WHERE problem_type IS NOT NULL GROUP BY problem_type"
        ).fetchall()
        
        # Средняя уверенность модели
        avg_confidence = cursor.execute(
            "SELECT AVG(confidence) as avg_conf FROM tickets WHERE confidence IS NOT NULL"
        ).fetchone()[0] or 0.0
        
        # Процент автоматических решений
        auto_rate = (auto_closed / total_tickets * 100) if total_tickets > 0 else 0.0
        
    except sqlite3.OperationalError:
         # Return zero values if DB is empty or not init
         return {
            "total_tickets": 0,
            "closed_tickets": 0,
            "auto_closed_tickets": 0,
            "tickets_by_classification": {},
            "tickets_by_queue": {},
            "tickets_by_problem_type": {},
            "accuracy_metrics": {"avg_confidence": 0.0},
            "auto_resolution_rate": 0.0,
            "avg_response_time": 0.0
         }
    finally:
        conn.close()

    return {
        "total_tickets": total_tickets,
        "closed_tickets": closed_tickets,
        "auto_closed_tickets": auto_closed,
        "tickets_by_classification": {row['category']: row['count'] for row in classifications},
        "tickets_by_queue": {row['queue']: row['count'] for row in queues},
        "tickets_by_problem_type": {row['problem_type']: row['count'] for row in problem_types},
        "accuracy_metrics": {
            "avg_confidence": round(float(avg_confidence) * 100, 2) if avg_confidence else 0.0
        },
        "auto_resolution_rate": round(auto_rate, 2),
        "avg_response_time": 0.8  # Имитация времени ответа (в секундах)
    }
