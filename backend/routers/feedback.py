"""
Feedback router - обработка CSAT обратной связи
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from database import get_db
from schemas.feedback import FeedbackCreate, FeedbackResponse
from models.feedback import Feedback
from models.ticket import Ticket
from models.user import User

router = APIRouter(prefix="/tickets", tags=["feedback"])


@router.post("/{ticket_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(
    ticket_id: UUID,
    feedback_data: FeedbackCreate,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    Отправляет CSAT обратную связь для тикета
    """
    # Проверяем, существует ли тикет
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Проверяем, не отправлена ли уже обратная связь
    existing_feedback = db.query(Feedback).filter(Feedback.ticket_id == ticket_id).first()
    if existing_feedback:
        raise HTTPException(
            status_code=400, 
            detail="Feedback already submitted for this ticket"
        )
    
    # Получаем пользователя из токена (если есть)
    user_id = None
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
                        user_id = None
        except Exception as e:
            print(f"Error getting user from token: {e}")
    
    # Создаем обратную связь
    feedback = Feedback(
        ticket_id=ticket_id,
        user_id=user_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return FeedbackResponse(
        id=str(feedback.id),
        ticket_id=str(feedback.ticket_id),
        user_id=str(feedback.user_id) if feedback.user_id else None,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at.isoformat()
    )


@router.get("/{ticket_id}/feedback", response_model=Optional[FeedbackResponse])
def get_feedback(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получает обратную связь для тикета (если есть)
    """
    # Проверяем, существует ли тикет
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    feedback = db.query(Feedback).filter(Feedback.ticket_id == ticket_id).first()
    
    if not feedback:
        return None
    
    return FeedbackResponse(
        id=str(feedback.id),
        ticket_id=str(feedback.ticket_id),
        user_id=str(feedback.user_id) if feedback.user_id else None,
        rating=feedback.rating,
        comment=feedback.comment,
        created_at=feedback.created_at.isoformat()
    )

