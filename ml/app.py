"""
FastAPI сервис для ML классификации и автоответа
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import sys

# Добавляем текущую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sentence_transformers import SentenceTransformer
import joblib
from auto_reply import AutoReplyService
from improved_auto_reply import ImprovedAutoReplyService

app = FastAPI(
    title="Help Desk ML Service",
    description="Сервис классификации тикетов и автоматического ответа",
    version="1.0.0"
)

# Глобальные переменные для моделей
classifier_category = None
classifier_priority = None
classifier_problem_type = None
embedding_model = None
auto_reply_service = None
improved_auto_reply_service = None  # Улучшенный сервис с LLM


class TicketRequest(BaseModel):
    """Модель запроса для классификации тикета"""
    text: str
    subject: Optional[str] = ""
    language: Optional[str] = None  # 'ru', 'kz', или None для автоопределения


class AutoReplyRequest(BaseModel):
    """Модель запроса для автоответа"""
    text: str
    category: Optional[str] = None
    problem_type: Optional[str] = None
    language: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None  # История диалога для контекста


class PredictionResponse(BaseModel):
    """Модель ответа классификации"""
    category: str
    priority: str
    problem_type: str
    confidence: Dict[str, float]


class AutoReplyResponse(BaseModel):
    """Модель ответа автоответа"""
    can_auto_reply: bool
    response_text: Optional[str] = None
    response_id: Optional[str] = None
    similarity: Optional[float] = None
    reason: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None


def load_models():
    """Загружает все обученные модели"""
    global classifier_category, classifier_priority, classifier_problem_type, embedding_model, auto_reply_service, improved_auto_reply_service
    
    models_dir = "models"
    
    if not os.path.exists(models_dir):
        raise FileNotFoundError(f"Директория {models_dir} не найдена! Сначала обучите модели.")
    
    print("=" * 60)
    print("ЗАГРУЗКА МОДЕЛЕЙ")
    print("=" * 60)
    
    # Загрузка модели эмбеддингов
    print("\n1. Загрузка модели эмбеддингов...")
    embedding_model_path = os.path.join(models_dir, "sentence_transformer_model")
    if os.path.exists(embedding_model_path):
        embedding_model = SentenceTransformer(embedding_model_path)
        print(f"   ✅ Модель загружена из {embedding_model_path}")
    else:
        # Используем предобученную модель
        print("   ⚠️  Локальная модель не найдена, используем предобученную...")
        embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("   ✅ Предобученная модель загружена")
    
    # Загрузка классификаторов
    print("\n2. Загрузка классификаторов...")
    
    category_path = os.path.join(models_dir, "classifier_category.pkl")
    priority_path = os.path.join(models_dir, "classifier_priority.pkl")
    problem_type_path = os.path.join(models_dir, "classifier_problem_type.pkl")
    
    if not os.path.exists(category_path):
        raise FileNotFoundError(f"Классификатор категорий не найден: {category_path}")
    if not os.path.exists(priority_path):
        raise FileNotFoundError(f"Классификатор приоритетов не найден: {priority_path}")
    if not os.path.exists(problem_type_path):
        raise FileNotFoundError(f"Классификатор типов проблем не найден: {problem_type_path}")
    
    classifier_category = joblib.load(category_path)
    classifier_priority = joblib.load(priority_path)
    classifier_problem_type = joblib.load(problem_type_path)
    
    print("   ✅ Все классификаторы загружены")
    
    # Инициализация сервиса автоответа (старый, для совместимости)
    print("\n3. Инициализация сервиса автоответа...")
    responses_path = "responses.json"
    if not os.path.exists(responses_path):
        print(f"   ⚠️  Файл {responses_path} не найден, автоответ будет недоступен")
        auto_reply_service = None
    else:
        try:
            auto_reply_service = AutoReplyService(
                responses_path=responses_path,
                model_path=embedding_model_path if os.path.exists(embedding_model_path) else None
            )
            print("   ✅ Сервис автоответа инициализирован")
        except Exception as e:
            print(f"   ⚠️  Ошибка инициализации автоответа: {e}")
            auto_reply_service = None
    
    # Инициализация улучшенного сервиса автоответа с LLM
    print("\n4. Инициализация улучшенного сервиса автоответа (LLM)...")
    if not os.path.exists(responses_path):
        print(f"   ⚠️  Файл {responses_path} не найден, улучшенный автоответ будет недоступен")
        improved_auto_reply_service = None
    else:
        try:
            improved_auto_reply_service = ImprovedAutoReplyService(
                responses_path=responses_path,
                model_path=embedding_model_path if os.path.exists(embedding_model_path) else None,
                similarity_threshold=0.50  # Понижен для лучшей работы с казахским языком
            )
            print("   ✅ Улучшенный сервис автоответа инициализирован")
        except Exception as e:
            print(f"   ⚠️  Ошибка инициализации улучшенного автоответа: {e}")
            improved_auto_reply_service = None
    
    print("\n" + "=" * 60)
    print("ВСЕ МОДЕЛИ ЗАГРУЖЕНЫ!")
    print("=" * 60)


@app.on_event("startup")
async def startup_event():
    """Загружает модели при запуске приложения"""
    load_models()


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "service": "Help Desk ML Service",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "Классификация тикета (POST)",
            "/auto_reply": "Автоматический ответ (POST)",
            "/predict_and_reply": "Классификация + автоответ (POST)",
            "/summarize_conversation": "Резюмирование диалога (POST)",
            "/health": "Проверка работоспособности (GET)",
            "/docs": "Документация API (Swagger UI)"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    models_loaded = all([
        classifier_category is not None,
        classifier_priority is not None,
        classifier_problem_type is not None,
        embedding_model is not None
    ])
    
    return {
        "status": "healthy" if models_loaded else "degraded",
        "models_loaded": models_loaded,
        "auto_reply_available": auto_reply_service is not None,
        "improved_auto_reply_available": improved_auto_reply_service is not None,
        "using_improved_service": improved_auto_reply_service is not None
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_ticket(request: TicketRequest):
    """
    Классифицирует тикет: определяет категорию, приоритет и тип проблемы
    
    Args:
        request: Запрос с текстом тикета
    
    Returns:
        Результат классификации
    """
    if embedding_model is None or classifier_category is None:
        raise HTTPException(status_code=503, detail="Модели не загружены!")
    
    try:
        # Объединяем subject и body
        full_text = f"{request.subject} {request.text}".strip()
        
        if not full_text:
            raise HTTPException(status_code=400, detail="Текст тикета не может быть пустым!")
        
        # Генерация эмбеддинга
        embedding = embedding_model.encode([full_text])
        
        # Классификация
        category = classifier_category.predict(embedding)[0]
        priority = classifier_priority.predict(embedding)[0]
        problem_type = classifier_problem_type.predict(embedding)[0]
        
        # Получение вероятностей (confidence)
        try:
            category_proba = classifier_category.predict_proba(embedding)[0]
            priority_proba = classifier_priority.predict_proba(embedding)[0]
            problem_type_proba = classifier_problem_type.predict_proba(embedding)[0]
            
            # Находим максимальные вероятности
            category_conf = float(max(category_proba))
            priority_conf = float(max(priority_proba))
            problem_type_conf = float(max(problem_type_proba))
        except:
            # Если predict_proba недоступен, используем дефолтные значения
            category_conf = 0.8
            priority_conf = 0.8
            problem_type_conf = 0.8
        
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
        raise HTTPException(status_code=500, detail=f"Ошибка классификации: {str(e)}")


@app.post("/auto_reply", response_model=AutoReplyResponse)
async def get_auto_reply(request: AutoReplyRequest):
    """
    Получает автоматический ответ для тикета
    Использует улучшенный сервис с LLM генерацией (если доступен)
    
    Args:
        request: Запрос с текстом тикета и опциональными полями
    
    Returns:
        Автоматический ответ или причина отказа
    """
    # Всегда используем улучшенный сервис, если доступен
    if improved_auto_reply_service is None:
        if auto_reply_service is None:
            raise HTTPException(status_code=503, detail="Сервис автоответа недоступен!")
        # Fallback на старый сервис
        service = auto_reply_service
    else:
        service = improved_auto_reply_service
    
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Текст тикета не может быть пустым!")
        
        # Если problem_type не указан, пытаемся определить через классификацию
        if request.problem_type is None:
            if embedding_model is None or classifier_problem_type is None:
                # Не можем определить, считаем сложным для безопасности
                problem_type = "Сложный"
            else:
                embedding = embedding_model.encode([request.text])
                problem_type = classifier_problem_type.predict(embedding)[0]
        else:
            problem_type = request.problem_type
        
        # Получение автоответа (используем улучшенный метод, если доступен)
        if improved_auto_reply_service is not None:
            result = improved_auto_reply_service.generate_draft_reply(
                query=request.text,
                category=request.category,
                problem_type=problem_type,
                language=request.language,
                conversation_history=request.conversation_history
            )
        else:
            result = auto_reply_service.get_auto_reply(
                query=request.text,
                problem_type=problem_type,
                category=request.category,
                language=request.language
            )
        
        return AutoReplyResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения автоответа: {str(e)}")


@app.post("/predict_and_reply")
async def predict_and_reply(request: TicketRequest):
    """
    Комбинированный эндпоинт: классификация + автоответ
    
    Args:
        request: Запрос с текстом тикета
    
    Returns:
        Результат классификации и автоответ (если возможен)
    """
    # Классификация
    prediction = await predict_ticket(request)
    
    # Попытка автоответа
    auto_reply_result = None
    service = improved_auto_reply_service if improved_auto_reply_service is not None else auto_reply_service
    if service is not None:
        try:
            auto_reply_result = await get_auto_reply(AutoReplyRequest(
                text=request.text,
                category=prediction.category,
                problem_type=prediction.problem_type,
                language=request.language
            ))
        except:
            pass
    
    return {
        "prediction": prediction.dict(),
        "auto_reply": auto_reply_result.dict() if auto_reply_result else None
    }


class SummarizeRequest(BaseModel):
    """Модель запроса для резюмирования диалога"""
    messages: List[Dict]  # Список сообщений диалога
    language: Optional[str] = None


class SummarizeResponse(BaseModel):
    """Модель ответа резюмирования"""
    summary: str
    language: str


@app.post("/summarize_conversation", response_model=SummarizeResponse)
async def summarize_conversation(request: SummarizeRequest):
    """
    Резюмирует диалог для передачи специалисту
    Согласно imporvemnt.md: резюмирование диалогов через LLM
    """
    if improved_auto_reply_service is None:
        raise HTTPException(status_code=503, detail="Улучшенный сервис автоответа недоступен!")
    
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Список сообщений не может быть пустым!")
        
        summary = improved_auto_reply_service.summarize_conversation(
            messages=request.messages,
            language=request.language
        )
        
        language = request.language or improved_auto_reply_service._detect_language(
            request.messages[0].get('text', '')
        )
        
        return SummarizeResponse(summary=summary, language=language)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка резюмирования: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("ЗАПУСК ML СЕРВИСА")
    print("=" * 60)
    print("\nСервис будет доступен по адресу: http://localhost:8000")
    print("Документация API: http://localhost:8000/docs")
    print("\n" + "=" * 60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

