"""
TicketHistory router - история изменений тикета
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from schemas.ticket_history import TicketHistoryResponse
from models.ticket_history import TicketHistory, HistoryAction
from models.ticket import Ticket
from models.user import User

router = APIRouter(prefix="/tickets", tags=["ticket-history"])


@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
def get_ticket_history(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Получает историю изменений тикета
    """
    # Проверяем, существует ли тикет
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Получаем историю
    history_items = db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket_id
    ).order_by(TicketHistory.created_at.asc()).all()
    
    result = []
    for item in history_items:
        user_name = None
        if item.user_id:
            user = db.query(User).filter(User.id == item.user_id).first()
            if user:
                user_name = user.name or user.email
        
        result.append(TicketHistoryResponse(
            id=str(item.id),
            ticket_id=str(item.ticket_id),
            user_id=str(item.user_id) if item.user_id else None,
            action=item.action.value,
            old_value=item.old_value,
            new_value=item.new_value,
            description=item.description,
            created_at=item.created_at.isoformat(),
            user_name=user_name
        ))
    
    return result

