"""
Tickets router - обработка тикетов
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from database import get_db
from schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from schemas.comment import CommentCreate, CommentResponse
from models.ticket import Ticket, TicketStatus
from models.ticket_message import TicketMessage
from models.category import Category
from models.user import User
from models.ai_prediction import AIPrediction
from models.ai_auto_response import AIAutoResponse
from models.ml_model import MLModel
from services.ai_classifier import AIClassifier
from services.ai_router import AIRouter
from services.auto_resolver import AutoResolver
from services.stats_service import StatsService
from services.sla_service import SLAService
from utils.history import log_ticket_creation, log_status_change, log_priority_change, log_assignment

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
    
    # Рассчитываем SLA дедлайн
    if ml_result["priority"]:
        ticket.sla_deadline = SLAService.calculate_sla_deadline(
            ml_result["priority"],
            ticket.created_at
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
    
    # Записываем создание тикета в историю
    log_ticket_creation(ticket, db, ticket_data.user_id)
    
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
    
    # 8. Создаем уведомления для всех админов о новом тикете
    from models.notification import Notification, NotificationType
    from models.user import UserRole
    
    admins = db.query(User).filter(User.role == UserRole.ADMIN.value).all()
    
    for admin in admins:
        notification = Notification(
            user_id=admin.id,
            ticket_id=ticket.id,
            notification_type=NotificationType.TICKET_CREATED,
            title=f"Новый тикет #{str(ticket.id)[:8]}",
            message=f"Создан новый тикет: {ticket.subject or ticket.body[:100]}..."
        )
        db.add(notification)
    
    db.commit()
    db.refresh(ticket)
    
    # 9. Обновляем статистику
    try:
        stats_service.update_daily_stats(db)
    except Exception as e:
        print(f"Warning: Could not update daily stats: {e}")
    
    return ticket


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    skip: int = 0,
    limit: int = 50,
    status: Optional[TicketStatus] = None,
    category_id: Optional[UUID] = None,
    category_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Список тикетов с фильтрацией"""
    query = db.query(Ticket)
    
    if status:
        query = query.filter(Ticket.status == status)
    
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    elif category_name:
        # Ищем категорию по имени (точное совпадение или частичное)
        category = db.query(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        ).first()
        if category:
            query = query.filter(Ticket.category_id == category.id)
        else:
            # Если категория не найдена, возвращаем пустой результат
            print(f"Category not found: {category_name}")
            return []
    
    if date_from:
        try:
            # Парсим дату в формате YYYY-MM-DD
            if 'T' in date_from:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            else:
                # Если только дата без времени, добавляем время начала дня
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= date_from_obj)
        except Exception as e:
            print(f"Error parsing date_from: {e}, value: {date_from}")
            pass
    
    if date_to:
        try:
            # Парсим дату в формате YYYY-MM-DD
            if 'T' in date_to:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                # Если только дата без времени, добавляем время конца дня
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Добавляем один день, чтобы включить весь день
            from datetime import timedelta
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(Ticket.created_at < date_to_obj)
        except Exception as e:
            print(f"Error parsing date_to: {e}, value: {date_to}")
            pass
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
    return tickets


@router.get("/search", response_model=List[TicketResponse])
def search_tickets(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[TicketStatus] = None,
    category_id: Optional[UUID] = None,
    category_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Поиск тикетов по тексту в subject и body с фильтрацией"""
    if not q or len(q.strip()) == 0:
        # Если поисковый запрос пустой, возвращаем обычный список с фильтрами
        query = db.query(Ticket)
        if status:
            query = query.filter(Ticket.status == status)
        if category_id:
            query = query.filter(Ticket.category_id == category_id)
        elif category_name:
            category = db.query(Category).filter(
                Category.name.ilike(f"%{category_name}%")
            ).first()
            if category:
                query = query.filter(Ticket.category_id == category.id)
            else:
                print(f"Category not found in search: {category_name}")
                return []
        if date_from:
            try:
                if 'T' in date_from:
                    date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                else:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Ticket.created_at >= date_from_obj)
            except Exception as e:
                print(f"Error parsing date_from in search empty: {e}, value: {date_from}")
                pass
        if date_to:
            try:
                if 'T' in date_to:
                    date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                else:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                from datetime import timedelta
                date_to_obj = date_to_obj + timedelta(days=1)
                query = query.filter(Ticket.created_at < date_to_obj)
            except Exception as e:
                print(f"Error parsing date_to in search empty: {e}, value: {date_to}")
                pass
        tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
        return tickets
    
    search_term = f"%{q.strip()}%"
    
    # Ищем в subject и body тикета (case-insensitive)
    query = db.query(Ticket).filter(
        (Ticket.subject.ilike(search_term)) | 
        (Ticket.body.ilike(search_term))
    )
    
    # Применяем фильтры
    if status:
        query = query.filter(Ticket.status == status)
    
    if category_id:
        query = query.filter(Ticket.category_id == category_id)
    elif category_name:
        category = db.query(Category).filter(
            Category.name.ilike(f"%{category_name}%")
        ).first()
        if category:
            query = query.filter(Ticket.category_id == category.id)
        else:
            print(f"Category not found in search empty: {category_name}")
            return []
    
    if date_from:
        try:
            if 'T' in date_from:
                date_from_obj = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            else:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Ticket.created_at >= date_from_obj)
        except Exception as e:
            print(f"Error parsing date_from in search main: {e}, value: {date_from}")
            pass
    
    if date_to:
        try:
            if 'T' in date_to:
                date_to_obj = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            else:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            from datetime import timedelta
            date_to_obj = date_to_obj + timedelta(days=1)
            query = query.filter(Ticket.created_at < date_to_obj)
        except Exception as e:
            print(f"Error parsing date_to in search main: {e}, value: {date_to}")
            pass
    
    tickets = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()
    return tickets


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


@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: UUID,
    update_data: TicketUpdate,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """Обновляет тикет"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Проверяем права доступа, если пользователь пытается закрыть тикет
    if update_data.status == TicketStatus.CLOSED:
        # Получаем текущего пользователя из токена
        current_user = None
        if authorization:
            try:
                from routers.auth import active_tokens
                if authorization.startswith("Bearer "):
                    token = authorization.split(" ")[1]
                else:
                    token = authorization
                
                token_data = active_tokens.get(token)
                if token_data:
                    user_id = token_data["user_id"]
                    if isinstance(user_id, str):
                        try:
                            user_id = UUID(user_id)
                        except ValueError:
                            pass
                    current_user = db.query(User).filter(User.id == user_id).first()
            except Exception as e:
                print(f"Error getting user from token: {e}")
        
        # Если пользователь не админ, проверяем, что это его тикет
        if current_user and current_user.role != "admin":
            if str(ticket.user_id) != str(current_user.id):
                raise HTTPException(
                    status_code=403, 
                    detail="You can only close your own tickets"
                )
    
    # Записываем изменения в историю
    if update_data.status and update_data.status != ticket.status:
        old_status = ticket.status
        ticket.status = update_data.status
        if update_data.status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.utcnow()
        log_status_change(ticket, old_status, update_data.status, db, current_user.id if current_user else None)
    
    if update_data.priority and update_data.priority != ticket.priority:
        old_priority = ticket.priority
        ticket.priority = update_data.priority
        # Пересчитываем SLA с новым приоритетом
        ticket.sla_deadline = SLAService.calculate_sla_deadline(
            update_data.priority,
            ticket.created_at
        )
        log_priority_change(ticket, old_priority, update_data.priority, db, current_user.id if current_user else None)
    
    if update_data.category_id:
        ticket.category_id = update_data.category_id
    
    if update_data.assigned_department_id:
        ticket.assigned_department_id = update_data.assigned_department_id
    
    if update_data.assigned_operator_id and update_data.assigned_operator_id != ticket.assigned_operator_id:
        log_assignment(ticket, update_data.assigned_operator_id, db, current_user.id if current_user else None)
        ticket.assigned_operator_id = update_data.assigned_operator_id
    
    # Проверяем и эскалируем тикет при необходимости
    if SLAService.should_escalate(ticket):
        SLAService.escalate_ticket(ticket, db, current_user.id if current_user else None)
    
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


