"""
FastAPI сервис для классификации тикетов и автоответа
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import joblib
import os
from typing import Optional
import numpy as np

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

# Модели для автоответа (можно расширить)
sample_responses = {
    "Техническая поддержка": [
        "Спасибо за обращение. Наша техническая команда уже работает над решением вашей проблемы.",
        "Мы получили ваш запрос. Технический специалист свяжется с вами в ближайшее время.",
    ],
    "IT поддержка": [
        "Ваш запрос принят в работу. IT-отдел обработает его в течение 24 часов.",
        "Спасибо за обращение. Мы уже работаем над решением вашей IT-проблемы.",
    ],
    "Биллинг и платежи": [
        "Ваш запрос по биллингу получен. Мы обработаем его в течение 1-2 рабочих дней.",
        "Спасибо за обращение. Финансовый отдел рассмотрит ваш вопрос.",
    ],
    "Клиентский сервис": [
        "Благодарим за обращение. Наш специалист свяжется с вами в ближайшее время.",
        "Ваш запрос принят. Мы ответим вам в течение рабочего дня.",
    ],
}

# Загрузка моделей при старте
@app.on_event("startup")
async def load_models():
    global model, clf_category, clf_priority, clf_problem_type
    
    print("Загрузка моделей...")
    
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
    clf_category = joblib.load("models/classifier_category.pkl")
    clf_priority = joblib.load("models/classifier_priority.pkl")
    clf_problem_type = joblib.load("models/classifier_problem_type.pkl")
    
    print("✅ Все модели загружены!")

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

class AutoReplyResponse(BaseModel):
    reply: str
    category: str

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
        ])
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
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Модели не загружены")
    
    try:
        # Если категория не указана, определяем её
        if request.category:
            category = request.category
        else:
            # Используем упрощенный подход: классифицируем текст
            embedding = model.encode([request.text])
            category = clf_category.predict(embedding)[0]
        
        # Выбираем ответ из шаблонов для данной категории
        if category in sample_responses:
            # Простой подход: берем первый шаблон
            # В будущем можно использовать семантический поиск
            reply = sample_responses[category][0]
        else:
            # Универсальный ответ
            reply = "Спасибо за обращение. Ваш запрос принят в работу. Мы свяжемся с вами в ближайшее время."
        
        return AutoReplyResponse(
            reply=reply,
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ответа: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

