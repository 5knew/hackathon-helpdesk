"""
Schemas for ticket comments (messages)
"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any


class CommentCreate(BaseModel):
    """Схема для создания комментария"""
    comment_text: str
    is_auto_reply: bool = False


class CommentResponse(BaseModel):
    """Схема ответа для комментария"""
    id: str
    ticket_id: str
    user_id: str
    user_name: Optional[str] = None  # Имя пользователя
    user_email: Optional[str] = None  # Email пользователя
    user_role: Optional[str] = None  # Роль пользователя (admin, employee, client)
    comment_text: str
    is_auto_reply: bool
    created_at: str
    
    class Config:
        from_attributes = True

