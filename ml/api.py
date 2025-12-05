"""
FastAPI сервис для классификации тикетов и автоответа
Использует FAISS для семантического поиска автоответов
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import joblib
import os
import sys
from typing import Optional, Dict
import numpy as np

# Добавляем путь для импорта auto_reply
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_reply import AutoReplyService

app = FastAPI(
    title="Helpdesk ML Service",
    description="Сервис классификации тикетов и автоответа",
    version="1.0.0"
)

# Глобальные переменные для моделей
model = None
clf_category = None
clf_priority = None
clf_problem_type = None
auto_reply_service = None  # FAISS сервис для автоответа

# Загрузка моделей при старте
@app.on_event("startup")
async def load_models():
    global model, clf_category, clf_priority, clf_problem_type, auto_reply_service
    
    print("=" * 60)
    print("ЗАГРУЗКА МОДЕЛЕЙ")
    print("=" * 60)
    
    # Загрузка модели эмбеддингов
    model_path = "models/sentence_transformer_model"
    if os.path.exists(model_path):
        model = SentenceTransformer(model_path)
        print(f"✅ Модель эмбеддингов загружена из {model_path}")
    else:
        # Если сохраненной модели нет, загружаем из HuggingFace
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("✅ Модель эмбеддингов загружена из HuggingFace")
    
    # Загрузка классификаторов
    print("\nЗагрузка классификаторов...")
    clf_category = joblib.load("models/classifier_category.pkl")
    clf_priority = joblib.load("models/classifier_priority.pkl")
    clf_problem_type = joblib.load("models/classifier_problem_type.pkl")
    print("✅ Классификаторы загружены")
    
    # Загрузка сервиса автоответа с FAISS
    print("\nИнициализация сервиса автоответа (FAISS)...")
    try:
        auto_reply_service = AutoReplyService(
            responses_path="responses.json",
            model_path=model_path if os.path.exists(model_path) else None,
            similarity_threshold=0.65
        )
        print("✅ Сервис автоответа инициализирован")
    except Exception as e:
        print(f"⚠️  Ошибка при загрузке сервиса автоответа: {e}")
        print("   Будет использован упрощенный режим")
        auto_reply_service = None
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ МОДЕЛИ ЗАГРУЖЕНЫ!")
    print("=" * 60)

# Модели запросов
class TicketRequest(BaseModel):
    subject: str
    body: str

class PredictionResponse(BaseModel):
    category: str
    priority: str
    problem_type: str
    confidence: dict

class AutoReplyRequest(BaseModel):
    text: str
    category: Optional[str] = None
    problem_type: Optional[str] = None
    language: Optional[str] = None  # 'ru' или 'kz'

class AutoReplyResponse(BaseModel):
    reply: str
    category: str
    can_auto_reply: Optional[bool] = True
    similarity: Optional[float] = None

# Эндпоинты
@app.get("/")
async def root():
    return {
        "message": "Helpdesk ML Service",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "Классификация тикета",
            "/auto_reply": "Автоответ на основе текста",
            "/health": "Проверка здоровья сервиса"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models_loaded": all([
            model is not None,
            clf_category is not None,
            clf_priority is not None,
            clf_problem_type is not None
        ]),
        "auto_reply_service_loaded": auto_reply_service is not None
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_ticket(ticket: TicketRequest):
    """
    Классификация тикета: категория, приоритет, тип проблемы
    """
    if model is None or clf_category is None:
        raise HTTPException(status_code=503, detail="Модели не загружены")
    
    try:
        # Объединяем subject и body
        text = f"{ticket.subject} {ticket.body}".strip()
        
        if not text:
            raise HTTPException(status_code=400, detail="Текст тикета не может быть пустым")
        
        # Генерируем эмбеддинг
        embedding = model.encode([text])
        
        # Предсказания
        category = clf_category.predict(embedding)[0]
        priority = clf_priority.predict(embedding)[0]
        problem_type = clf_problem_type.predict(embedding)[0]
        
        # Вероятности (confidence)
        category_proba = clf_category.predict_proba(embedding)[0]
        priority_proba = clf_priority.predict_proba(embedding)[0]
        problem_type_proba = clf_problem_type.predict_proba(embedding)[0]
        
        # Получаем максимальные вероятности
        category_conf = float(np.max(category_proba))
        priority_conf = float(np.max(priority_proba))
        problem_type_conf = float(np.max(problem_type_proba))
        
        return PredictionResponse(
            category=category,
            priority=priority,
            problem_type=problem_type,
            confidence={
                "category": category_conf,
                "priority": priority_conf,
                "problem_type": problem_type_conf
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при классификации: {str(e)}")

@app.post("/auto_reply", response_model=AutoReplyResponse)
async def auto_reply(request: AutoReplyRequest):
    """
    Генерация автоответа на основе текста тикета
    Использует FAISS семантический поиск для поиска наиболее подходящего ответа
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Модели не загружены")
    
    try:
        # Если категория не указана, определяем её через классификацию
        if request.category:
            category = request.category
        else:
            embedding = model.encode([request.text])
            category = clf_category.predict(embedding)[0]
        
        # Если problem_type не указан, определяем его
        if request.problem_type is None:
            embedding = model.encode([request.text])
            problem_type = clf_problem_type.predict(embedding)[0]
        else:
            problem_type = request.problem_type
        
        # Используем FAISS сервис для поиска лучшего ответа
        if auto_reply_service is not None:
            result = auto_reply_service.get_auto_reply(
                query=request.text,
                problem_type=problem_type,
                category=category,
                language=request.language
            )
            
            if result.get('can_auto_reply', False):
                return AutoReplyResponse(
                    reply=result.get('response_text', 'Спасибо за обращение. Ваш запрос принят в работу.'),
                    category=result.get('category', category),
                    can_auto_reply=True,
                    similarity=result.get('similarity', 0.0)
                )
            else:
                # Не можем ответить автоматически, возвращаем стандартный ответ
                return AutoReplyResponse(
                    reply="Спасибо за обращение. Ваш запрос принят в работу. Наш специалист свяжется с вами в ближайшее время.",
                    category=category,
                    can_auto_reply=False,
                    similarity=result.get('similarity', 0.0)
                )
        else:
            # Fallback: упрощенный режим без FAISS
            fallback_responses = {
                "Техническая поддержка": "Спасибо за обращение. Наша техническая команда уже работает над решением вашей проблемы.",
                "IT поддержка": "Ваш запрос принят в работу. IT-отдел обработает его в течение 24 часов.",
                "Биллинг и платежи": "Ваш запрос по биллингу получен. Мы обработаем его в течение 1-2 рабочих дней.",
                "Клиентский сервис": "Благодарим за обращение. Наш специалист свяжется с вами в ближайшее время.",
            }
            
            reply = fallback_responses.get(category, "Спасибо за обращение. Ваш запрос принят в работу. Мы свяжемся с вами в ближайшее время.")
            
            return AutoReplyResponse(
                reply=reply,
                category=category,
                can_auto_reply=(problem_type == "Типовой"),
                similarity=0.0
            )
            
    except Exception as e:
        import traceback
        print(f"Ошибка при генерации автоответа: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ответа: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

