"""
Comments router - обработка комментариев к тикетам
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database import get_db
from schemas.comment import CommentCreate, CommentResponse
from models.ticket import Ticket
from models.ticket_message import TicketMessage
from models.user import User, UserRole
from models.notification import Notification, NotificationType
from routers.auth import active_tokens
from utils.history import log_comment_added

router = APIRouter(prefix="/tickets", tags=["comments"])


def get_current_user_from_token(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Получает текущего пользователя из токена"""
    if not authorization:
        return None
    
    try:
        # Извлекаем токен из заголовка "Bearer <token>"
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Проверяем токен
        token_data = active_tokens.get(token)
        if not token_data:
            return None
        
        user_id = token_data["user_id"]
        # Преобразуем user_id в UUID если это строка
        from uuid import UUID as UUIDType
        if isinstance(user_id, str):
            try:
                user_id = UUIDType(user_id)
            except ValueError:
                pass
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        print(f"Error getting user from token: {e}")
        return None


@router.post("/{ticket_id}/comments", response_model=CommentResponse)
def add_comment(
    ticket_id: UUID,
    comment_data: CommentCreate,
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """Добавляет комментарий к тикету"""
    # Проверяем, существует ли тикет
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Получаем текущего пользователя из токена или используем user_id из тикета
    current_user = get_current_user_from_token(authorization, db)
    if current_user:
        user_id = current_user.id
        print(f"Comment from authenticated user: {current_user.email} (role: {current_user.role})")
    else:
        # Fallback: используем user_id из тикета (для обратной совместимости)
        user_id = ticket.user_id
        print(f"Comment from ticket owner (no auth token): {user_id}")
    
    # Создаем сообщение (комментарий)
    message = TicketMessage(
        ticket_id=ticket_id,
        sender_id=user_id,
        text=comment_data.comment_text,
        attachments=None
    )
    
    try:
        db.add(message)
        db.flush()  # Получаем ID сообщения
        
        # Определяем роль отправителя
        sender_role = current_user.role if current_user else None
        if not sender_role:
            # Если нет current_user, проверяем по user_id
            sender_user = db.query(User).filter(User.id == user_id).first()
            sender_role = sender_user.role if sender_user else None
        
        # Логика уведомлений:
        # 1. Если пользователь комментирует -> уведомляем всех админов (кроме себя)
        # 2. Если админ/оператор комментирует -> уведомляем владельца тикета
        if sender_role == UserRole.ADMIN.value or sender_role == UserRole.EMPLOYEE.value:
            # Админ или оператор ответил - уведомляем владельца тикета
            if ticket.user_id != user_id:  # Не отправляем уведомление самому себе
                admin_notification = Notification(
                    user_id=ticket.user_id,
                    ticket_id=ticket_id,
                    notification_type=NotificationType.ADMIN_REPLY,
                    title=f"Администратор ответил на ваш вопрос #{str(ticket_id)[:8]}",
                    message=f"Получен ответ от администратора: {comment_data.comment_text[:100]}..."
                )
                db.add(admin_notification)
        else:
            # Пользователь комментирует - уведомляем всех админов
            admins = db.query(User).filter(User.role == UserRole.ADMIN.value).all()
            
            for admin in admins:
                # Не отправляем уведомление самому отправителю, если он админ
                if admin.id != user_id:
                    notification = Notification(
                        user_id=admin.id,
                        ticket_id=ticket_id,
                        notification_type=NotificationType.COMMENT,
                        title=f"Новый комментарий в тикете #{str(ticket_id)[:8]}",
                        message=f"Пользователь добавил комментарий: {comment_data.comment_text[:100]}..."
                    )
                    db.add(notification)
        
        # Записываем добавление комментария в историю
        log_comment_added(ticket, db, user_id)
        
        db.commit()
        db.refresh(message)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating comment: {str(e)}")
    
    # Получаем информацию о пользователе (используем current_user если есть, иначе sender)
    sender = current_user if current_user else db.query(User).filter(User.id == user_id).first()
    
    # Преобразуем в формат ответа
    return CommentResponse(
        id=str(message.id),
        ticket_id=str(message.ticket_id),
        user_id=str(message.sender_id),
        user_name=sender.name if sender else None,
        user_email=sender.email if sender else None,
        user_role=sender.role if sender else None,
        comment_text=message.text,
        is_auto_reply=comment_data.is_auto_reply,
        created_at=message.created_at.isoformat() if message.created_at else datetime.utcnow().isoformat()
    )


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def get_comments(
    ticket_id: UUID,
    db: Session = Depends(get_db)
):
    """Получает все комментарии для тикета"""
    # Проверяем, существует ли тикет
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Получаем все сообщения для тикета с информацией о пользователях
    messages = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at.asc()).all()
    
    # Преобразуем в формат ответа с информацией о пользователях
    result = []
    for msg in messages:
        # Получаем информацию о пользователе
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        
        result.append(CommentResponse(
            id=str(msg.id),
            ticket_id=str(msg.ticket_id),
            user_id=str(msg.sender_id),
            user_name=sender.name if sender else None,
            user_email=sender.email if sender else None,
            user_role=sender.role if sender else None,
            comment_text=msg.text,
            is_auto_reply=False,
            created_at=msg.created_at.isoformat() if msg.created_at else datetime.utcnow().isoformat()
        ))
    
    return result
