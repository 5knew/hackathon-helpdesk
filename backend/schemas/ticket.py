"""
Pydantic schemas for Ticket
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from models.ticket import TicketSource, TicketLanguage, TicketPriority, TicketStatus, IssueType


class TicketCreate(BaseModel):
    """Схема для создания тикета"""
    source: TicketSource
    user_id: UUID
    subject: Optional[str] = None
    body: str
    language: TicketLanguage = TicketLanguage.RU


class TicketResponse(BaseModel):
    """Схема ответа с тикетом"""
    id: UUID
    source: TicketSource
    user_id: UUID
    subject: Optional[str]
    body: str
    language: TicketLanguage
    category_id: Optional[UUID]
    priority: Optional[TicketPriority]
    issue_type: Optional[IssueType]
    ai_confidence: Optional[float]
    assigned_department_id: Optional[UUID]
    assigned_operator_id: Optional[UUID]
    status: TicketStatus
    auto_resolved: bool
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    sla_deadline: Optional[datetime] = None
    is_escalated: bool = False
    
    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    """Схема для обновления тикета"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category_id: Optional[UUID] = None
    assigned_department_id: Optional[UUID] = None
    assigned_operator_id: Optional[UUID] = None

