"""
Notifications router - управление уведомлениями
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from schemas.notification import NotificationResponse, NotificationUpdate
from models.notification import Notification
from models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_current_user_id(db: Session, user_id: str = None) -> UUID:
    """
    Получает ID текущего пользователя
    TODO: Интегрировать с системой аутентификации
    Пока используем user_id из параметра
    """
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получает уведомления пользователя"""
    current_user_id = get_current_user_id(db, user_id)
    
    # Проверяем, существует ли пользователь
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = db.query(Notification).filter(Notification.user_id == current_user_id)
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return [
        NotificationResponse(
            id=str(n.id),
            user_id=str(n.user_id),
            ticket_id=str(n.ticket_id) if n.ticket_id else None,
            notification_type=n.notification_type.value,
            title=n.title,
            message=n.message,
            is_read=n.is_read,
            created_at=n.created_at.isoformat() if n.created_at else ""
        )
        for n in notifications
    ]


@router.get("/unread/count")
def get_unread_count(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Получает количество непрочитанных уведомлений"""
    current_user_id = get_current_user_id(db, user_id)
    
    count = db.query(Notification).filter(
        Notification.user_id == current_user_id,
        Notification.is_read == False
    ).count()
    
    return {"count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: UUID,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Помечает уведомление как прочитанное"""
    current_user_id = get_current_user_id(db, user_id)
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    
    return NotificationResponse(
        id=str(notification.id),
        user_id=str(notification.user_id),
        ticket_id=str(notification.ticket_id) if notification.ticket_id else None,
        notification_type=notification.notification_type.value,
        title=notification.title,
        message=notification.message,
        is_read=notification.is_read,
        created_at=notification.created_at.isoformat() if notification.created_at else ""
    )


@router.put("/read-all")
def mark_all_as_read(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Помечает все уведомления пользователя как прочитанные"""
    current_user_id = get_current_user_id(db, user_id)
    
    updated = db.query(Notification).filter(
        Notification.user_id == current_user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"updated": updated}


