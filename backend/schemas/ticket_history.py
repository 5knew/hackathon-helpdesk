"""
TicketHistory schemas - схемы для истории изменений тикета
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TicketHistoryResponse(BaseModel):
    """Схема ответа с историей изменений"""
    id: str
    ticket_id: str
    user_id: Optional[str] = None
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: Optional[str] = None
    created_at: str
    user_name: Optional[str] = None  # Имя пользователя, который изменил

    class Config:
        from_attributes = True

