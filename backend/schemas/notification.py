"""
Schemas for notifications
"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class NotificationResponse(BaseModel):
    """Схема ответа для уведомления"""
    id: str
    user_id: str
    ticket_id: Optional[str]
    notification_type: str
    title: str
    message: str
    is_read: bool
    created_at: str
    
    class Config:
        from_attributes = True


class NotificationUpdate(BaseModel):
    """Схема для обновления уведомления (например, пометить как прочитанное)"""
    is_read: bool


