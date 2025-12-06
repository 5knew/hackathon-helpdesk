"""
Feedback schemas - схемы для CSAT обратной связи
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class FeedbackCreate(BaseModel):
    """Схема для создания обратной связи"""
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: Optional[str] = Field(None, description="Комментарий пользователя")


class FeedbackResponse(BaseModel):
    """Схема ответа с обратной связью"""
    id: str
    ticket_id: str
    user_id: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True

