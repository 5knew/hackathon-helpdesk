"""
Tickets router - обработка тикетов
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database import get_db
from schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from models.ticket import Ticket, TicketStatus
from models.category import Category
from models.user import User
from models.ai_prediction import AIPrediction
from models.ai_auto_response import AIAutoResponse
from models.ml_model import MLModel
from services.ai_classifier import AIClassifier
from services.ai_router import AIRouter
from services.auto_resolver import AutoResolver
from services.stats_service import StatsService

router = APIRouter(prefix="/tickets", tags=["tickets"])

# Инициализация сервисов
classifier = AIClassifier()
router_service = AIRouter()
auto_resolver = AutoResolver()
stats_service = StatsService()


@router.post("/create", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db)
):
    """
    Создает новый тикет и автоматически обрабатывает его с помощью ИИ
    """
    # 0. Проверяем/создаем пользователя
    user = db.query(User).filter(User.id == ticket_data.user_id).first()
    if not user:
        # Создаем пользователя автоматически, если его нет
        user = User(
            id=ticket_data.user_id,
            email=f"user_{ticket_data.user_id}@example.com",  # Временный email
            name="Auto-created User",
            role="client"
        )
        db.add(user)
        db.flush()
    
    # 1. AI Classifier - классификация тикета
    ml_result = classifier.classify(ticket_data.subject or "", ticket_data.body)
    
    # 2. Получаем или создаем категорию
    category = db.query(Category).filter(
        Category.name == ml_result["category"]
    ).first()
    
    if not category:
        # Создаем новую категорию, если её нет
        category = Category(
            name=ml_result["category"],
            description=f"Автоматически созданная категория"
        )
        db.add(category)
        db.flush()
    
    # 3. Получаем последнюю ML модель (или создаем дефолтную)
    ml_model = db.query(MLModel).order_by(MLModel.created_at.desc()).first()
    if not ml_model:
        ml_model = MLModel(
            name="default_classifier",
            version="1.0",
            description="Default ML model"
        )
        db.add(ml_model)
        db.flush()
    
    # 4. Создаем тикет
    ticket = Ticket(
        source=ticket_data.source,
        user_id=ticket_data.user_id,
        subject=ticket_data.subject,
        body=ticket_data.body,
        language=ticket_data.language,
        category_id=category.id,
        priority=ml_result["priority"],
        issue_type=ml_result["issue_type"],
        ai_confidence=ml_result["confidence"].get("problem_type", 0.5),
        status=TicketStatus.NEW
    )
    
    # 5. Маршрутизация
    if ml_result["confidence"].get("category", 0) >= 0.7:
        department_id = router_service.route_ticket(
            db,
            ml_result["category"],
            ml_result["priority"].value,
            ml_result["confidence"].get("category", 0)
        )
        if department_id:
            ticket.assigned_department_id = department_id
    
    db.add(ticket)
    db.flush()  # Получаем ticket.id
    
    # 6. Попытка автоматического решения
    if ml_result["issue_type"].value == "auto_resolvable":
        auto_response_text = auto_resolver.try_auto_resolve(
            ticket_data.body,
            ml_result["category"],
            ml_result["issue_type"]
        )
        
        if auto_response_text:
            ticket.status = TicketStatus.AUTO_RESOLVED
            ticket.auto_resolved = True
            ticket.closed_at = datetime.utcnow()
            
            # Сохраняем автоматический ответ
            auto_response = AIAutoResponse(
                ticket_id=ticket.id,
                response_text=auto_response_text,
                is_successful=True
            )
            db.add(auto_response)
    
    # 7. Сохраняем предсказание ИИ
    prediction = AIPrediction(
        ticket_id=ticket.id,
        model_id=ml_model.id,
        predicted_category_id=category.id,
        predicted_priority=ml_result["priority"],
        predicted_issue_type=ml_result["issue_type"],
        confidence=ml_result["confidence"].get("problem_type", 0.5)
    )
    db.add(prediction)
    
    db.commit()
    db.refresh(ticket)
    
    # 8. Обновляем статистику
    try:
        stats_service.update_daily_stats(db)
    except Exception as e:
        print(f"Warning: Could not update daily stats: {e}")
    
    return ticket


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает тикет по ID"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 50,
    status: Optional[TicketStatus] = None,
    db: Session = Depends(get_db)
):
    """Список тикетов с фильтрацией"""
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    
    tickets = query.offset(skip).limit(limit).all()
    return tickets


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: UUID,
    update_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    """Обновляет тикет"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if update_data.status:
        ticket.status = update_data.status
        if update_data.status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.utcnow()
    
    if update_data.priority:
        ticket.priority = update_data.priority
    
    if update_data.category_id:
        ticket.category_id = update_data.category_id
    
    if update_data.assigned_department_id:
        ticket.assigned_department_id = update_data.assigned_department_id
    
    if update_data.assigned_operator_id:
        ticket.assigned_operator_id = update_data.assigned_operator_id
    
    ticket.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(ticket)
    
    return ticket


@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """Удаляет тикет (soft delete - меняет статус на closed)"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Soft delete - помечаем как закрытый вместо физического удаления
    ticket.status = TicketStatus.CLOSED
    ticket.closed_at = datetime.utcnow()
    ticket.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Ticket deleted successfully", "ticket_id": str(ticket_id)}

