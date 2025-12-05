from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import sqlite3
import requests
import os
import re
from datetime import datetime, timedelta

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
    needs_clarification: bool = False  # Требуется уточнение при низкой уверенности
    confidence_warning: Optional[str] = None  # Предупреждение о низкой уверенности

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
    routing_errors: Dict[str, int]  # Метрики ошибок маршрутизации
    routing_error_rate: float  # Процент ошибок маршрутизации
    csat_score: float  # Customer Satisfaction Score (0-100)
    avg_resolution_time_by_category: Dict[str, float]  # Среднее время обработки по категориям (в часах)
    trends: Dict[str, Dict[str, int]]  # Тренды по дням (последние 7 дней)

class SummarizeRequest(BaseModel):
    ticket_id: Optional[int] = None
    text: Optional[str] = None  # Если ticket_id не указан, можно передать текст напрямую
    max_sentences: int = 3  # Максимальное количество предложений в резюме

class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]  # Ключевые моменты
    original_length: int
    summary_length: int
    compression_ratio: float

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

def summarize_text(text: str, max_sentences: int = 3) -> Dict:
    """
    Резюмирует текст используя extractive summarization.
    Использует простой подход: выбирает наиболее важные предложения.
    """
    if not text or len(text.strip()) < 50:
        return {
            "summary": text,
            "key_points": [],
            "original_length": len(text),
            "summary_length": len(text),
            "compression_ratio": 1.0
        }
    
    # Разбиваем текст на предложения
    sentences = re.split(r'[.!?]+\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if len(sentences) <= max_sentences:
        # Если предложений мало, возвращаем весь текст
        key_points = [s[:100] + "..." if len(s) > 100 else s for s in sentences[:3]]
        return {
            "summary": text,
            "key_points": key_points,
            "original_length": len(text),
            "summary_length": len(text),
            "compression_ratio": 1.0
        }
    
    # Простой extractive summarization:
    # 1. Берем первые предложения (обычно содержат основную информацию)
    # 2. Берем предложения с ключевыми словами (проблема, ошибка, не могу, нужно и т.д.)
    # 3. Берем предложения с вопросами
    
    key_words = ['проблема', 'ошибка', 'не могу', 'не работает', 'нужно', 'требуется', 
                 'помогите', 'помощь', 'не получается', 'не удается', 'важно', 'срочно']
    
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        # Приоритет первым предложениям
        if i < 2:
            score += 2
        # Приоритет предложениям с ключевыми словами
        sentence_lower = sentence.lower()
        for keyword in key_words:
            if keyword in sentence_lower:
                score += 1
        # Приоритет предложениям с вопросами
        if '?' in sentence:
            score += 1
        # Приоритет более длинным предложениям (но не слишком длинным)
        if 20 < len(sentence) < 200:
            score += 0.5
        
        scored_sentences.append((score, i, sentence))
    
    # Сортируем по score и берем топ-N
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    selected_indices = sorted([x[1] for x in scored_sentences[:max_sentences]])
    summary_sentences = [sentences[i] for i in selected_indices]
    
    summary = '. '.join(summary_sentences)
    if summary and not summary.endswith('.'):
        summary += '.'
    
    # Извлекаем ключевые моменты (первые 3 предложения с высоким score)
    key_points = [sentences[i][:100] + "..." if len(sentences[i]) > 100 else sentences[i] 
                  for i in selected_indices[:3]]
    
    return {
        "summary": summary,
        "key_points": key_points,
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": round(len(summary) / len(text), 2) if text else 1.0
    }


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
        
        # 1.5. Валидация уверенности модели (если confidence < 0.7, требуется уточнение)
        CONFIDENCE_THRESHOLD = 0.7
        needs_clarification = False
        confidence_warning = None
        
        category_conf = confidence.get("category", 0.0)
        priority_conf = confidence.get("priority", 0.0)
        problem_type_conf = confidence.get("problem_type", 0.0)
        
        # Проверяем уверенность по каждому параметру
        low_confidence_fields = []
        if category_conf < CONFIDENCE_THRESHOLD:
            low_confidence_fields.append(f"категория ({category_conf:.1%})")
        if priority_conf < CONFIDENCE_THRESHOLD:
            low_confidence_fields.append(f"приоритет ({priority_conf:.1%})")
        if problem_type_conf < CONFIDENCE_THRESHOLD:
            low_confidence_fields.append(f"тип проблемы ({problem_type_conf:.1%})")
        
        if low_confidence_fields:
            needs_clarification = True
            confidence_warning = f"Низкая уверенность модели по: {', '.join(low_confidence_fields)}. Требуется ручная проверка."

        # 2. Routing Logic согласно ТЗ
        status = "Pending"
        message = "Заявка принята в обработку."
        queue = "General"
        
        # Если требуется уточнение, отправляем в специальную очередь
        if needs_clarification:
            queue = "ManualReview"
            message = f"Заявка требует уточнения. {confidence_warning} Категория: {category}, Приоритет: {priority}"

        # Улучшенная логика маршрутизации с учетом confidence scores
        # A. Проверка типа проблемы (Типовой = автоматическое решение)
        # Используем confidence по problem_type для более точного определения
        if problem_type == "Типовой" and problem_type_conf >= 0.75:
            # Высокая уверенность в типовом инциденте - автоматическое решение
            auto_reply = get_auto_reply_from_ml(ticket.problem_description, category, problem_type)
            if auto_reply:
                status = "Closed"
                queue = "Automated"
                message = auto_reply + f" (Автоматически закрыто. Категория: {category}, Уверенность: {problem_type_conf:.1%})"
            else:
                # Если не можем ответить автоматически, отправляем в общую очередь
                status = "Pending"
                queue = "GeneralSupport"
                message = f"Заявка принята в обработку. Категория: {category}"
        elif problem_type == "Типовой" and problem_type_conf < 0.75:
            # Низкая уверенность в типовом инциденте - требует проверки
            status = "Pending"
            queue = "GeneralSupport"
            message = f"Заявка принята. Возможно типовой случай (уверенность: {problem_type_conf:.1%}), требуется проверка. Категория: {category}"
        
        else:
            # B. Маршрутизация сложных кейсов в профильные департаменты
            # Используем confidence для взвешенной маршрутизации
            
            # Эскалация по приоритету (с учетом confidence)
            if priority == "Высокий":
                if priority_conf >= 0.7:
                    queue = "HighPriority"
                    message = f"Заявка эскалирована в отдел высокого приоритета. Категория: {category} (уверенность приоритета: {priority_conf:.1%})"
                else:
                    # Низкая уверенность в приоритете - отправляем в общую очередь с пометкой
                    queue = "HighPriority"
                    message = f"Заявка эскалирована (приоритет требует проверки, уверенность: {priority_conf:.1%}). Категория: {category}"
            
            # Маршрутизация по категории (с учетом confidence категории)
            elif category_conf >= 0.7:
                # Высокая уверенность в категории - используем для маршрутизации
                if "Биллинг" in category or "платеж" in category.lower():
                    queue = "Billing"
                    message = f"Заявка направлена в отдел биллинга. Приоритет: {priority} (уверенность категории: {category_conf:.1%})"
                elif "Техническая" in category or "IT" in category:
                    queue = "TechSupport"
                    message = f"Заявка направлена в техническую поддержку. Приоритет: {priority} (уверенность категории: {category_conf:.1%})"
                elif "HR" in category or "кадр" in category.lower():
                    queue = "HR"
                    message = f"Заявка направлена в HR отдел. Приоритет: {priority} (уверенность категории: {category_conf:.1%})"
                elif "Клиентский" in category or "сервис" in category.lower():
                    queue = "CustomerService"
                    message = f"Заявка направлена в клиентский сервис. Приоритет: {priority} (уверенность категории: {category_conf:.1%})"
                else:
                    queue = "GeneralSupport"
                    message = f"Заявка направлена в общую поддержку. Категория: {category}, Приоритет: {priority} (уверенность категории: {category_conf:.1%})"
            else:
                # Низкая уверенность в категории - отправляем в общую очередь для проверки
                queue = "GeneralSupport"
                message = f"Заявка направлена в общую поддержку для проверки категории (уверенность: {category_conf:.1%}). Предполагаемая категория: {category}, Приоритет: {priority}"

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
                needs_clarification INTEGER DEFAULT 0,
                confidence_warning TEXT,
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
        
        try:
            cursor.execute("ALTER TABLE tickets ADD COLUMN needs_clarification INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        try:
            cursor.execute("ALTER TABLE tickets ADD COLUMN confidence_warning TEXT")
        except sqlite3.OperationalError:
            pass  # Колонка уже существует
        
        # Получаем значение уверенности
        confidence_value = confidence.get("problem_type", 0.0) if isinstance(confidence, dict) else 0.0
        
        cursor.execute(
            """INSERT INTO tickets 
               (user_id, problem_description, priority, category, status, ml_classification, problem_type, queue, confidence, needs_clarification, confidence_warning) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ticket.user_id, ticket.problem_description, priority, category, status, 
             f"{category}|{priority}|{problem_type}", problem_type, queue, 
             confidence_value, 1 if needs_clarification else 0, confidence_warning)
        )
        ticket_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return TicketResponse(
            ticket_id=ticket_id, 
            status=status, 
            message=message, 
            queue=queue,
            needs_clarification=needs_clarification,
            confidence_warning=confidence_warning
        )
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
        
        # Метрики валидации уверенности
        tickets_needing_clarification = cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE needs_clarification = 1"
        ).fetchone()[0] or 0
        
        clarification_rate = (tickets_needing_clarification / total_tickets * 100) if total_tickets > 0 else 0.0
        
        # Метрики ошибок маршрутизации
        manual_review_tickets = cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE queue = 'ManualReview'"
        ).fetchone()[0] or 0
        
        low_confidence_tickets = cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE confidence < 0.7 AND confidence IS NOT NULL"
        ).fetchone()[0] or 0
        
        # Тикеты, которые были перемаршрутизированы (можно добавить поле reassigned в будущем)
        # Пока считаем ошибками маршрутизации тикеты в ManualReview и с низкой уверенностью
        routing_errors_count = manual_review_tickets  # Основной индикатор ошибок
        
        routing_error_rate = (routing_errors_count / total_tickets * 100) if total_tickets > 0 else 0.0
        
        routing_errors = {
            "manual_review": manual_review_tickets,
            "low_confidence": low_confidence_tickets,
            "needs_clarification": tickets_needing_clarification
        }
        
        # Расширенные метрики: CSAT Score
        # CSAT рассчитывается на основе: автоматических решений (высокий CSAT) и времени ответа
        # Формула: базовый CSAT (70) + бонус за автоответы (до +20) + бонус за скорость (до +10)
        csat_base = 70.0
        auto_bonus = min(auto_rate / 5, 20.0)  # До 20 баллов за автоответы
        speed_bonus = max(0, 10.0 - (avg_response_time * 10))  # До 10 баллов за скорость
        csat_score = min(100.0, csat_base + auto_bonus + speed_bonus)
        
        # Время обработки по категориям (в часах)
        resolution_times = cursor.execute("""
            SELECT category, 
                   AVG(CASE 
                       WHEN status = 'Closed' AND created_at IS NOT NULL 
                       THEN (julianday('now') - julianday(created_at)) * 24
                       ELSE NULL 
                   END) as avg_hours
            FROM tickets 
            WHERE category IS NOT NULL
            GROUP BY category
        """).fetchall()
        
        avg_resolution_time_by_category = {
            row['category']: round(float(row['avg_hours'] or 0.0), 2) 
            for row in resolution_times if row['avg_hours'] is not None
        }
        
        # Тренды: группировка по дням за последние 7 дней
        trends = {}
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            day_start = date + ' 00:00:00'
            day_end = date + ' 23:59:59'
            
            tickets_today = cursor.execute("""
                SELECT COUNT(*) as count 
                FROM tickets 
                WHERE created_at >= ? AND created_at <= ?
            """, (day_start, day_end)).fetchone()[0] or 0
            
            closed_today = cursor.execute("""
                SELECT COUNT(*) as count 
                FROM tickets 
                WHERE status = 'Closed' AND created_at >= ? AND created_at <= ?
            """, (day_start, day_end)).fetchone()[0] or 0
            
            trends[date] = {
                "total": tickets_today,
                "closed": closed_today
            }
        
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
            "avg_response_time": 0.0,
            "routing_errors": {},
            "routing_error_rate": 0.0,
            "csat_score": 0.0,
            "avg_resolution_time_by_category": {},
            "trends": {}
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
            "avg_confidence": round(float(avg_confidence) * 100, 2) if avg_confidence else 0.0,
            "tickets_needing_clarification": tickets_needing_clarification,
            "clarification_rate": round(clarification_rate, 2)
        },
        "auto_resolution_rate": round(auto_rate, 2),
        "avg_response_time": 0.8,  # Имитация времени ответа (в секундах)
        "routing_errors": routing_errors,
        "routing_error_rate": round(routing_error_rate, 2),
        "csat_score": round(csat_score, 2),
        "avg_resolution_time_by_category": avg_resolution_time_by_category,
        "trends": trends
    }

@app.post("/summarize", response_model=SummarizeResponse)
def summarize_ticket(request: SummarizeRequest):
    """
    Резюмирует переписку по тикету для оператора.
    Помогает операторам быстро понять суть проблемы.
    """
    try:
        text_to_summarize = None
        
        if request.ticket_id:
            # Получаем текст тикета из БД
            db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            ticket = cursor.execute(
                "SELECT problem_description, subject FROM tickets WHERE id = ?",
                (request.ticket_id,)
            ).fetchone()
            
            conn.close()
            
            if not ticket:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail=f"Тикет с ID {request.ticket_id} не найден")
            
            text_to_summarize = f"{ticket['subject']} {ticket['problem_description']}".strip()
        elif request.text:
            text_to_summarize = request.text
        else:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Необходимо указать ticket_id или text")
        
        # Резюмируем текст
        result = summarize_text(text_to_summarize, request.max_sentences)
        
        return SummarizeResponse(**result)
        
    except Exception as e:
        import traceback
        print(f"Error in summarize_ticket: {e}")
        print(traceback.format_exc())
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Ошибка при резюмировании: {str(e)}")
