"""
TicketHistory model - история изменений тикета (audit log)
"""
from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from database import Base


class HistoryAction(str, enum.Enum):
    """Типы действий в истории"""
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    PRIORITY_CHANGED = "priority_changed"
    ASSIGNED = "assigned"
    COMMENT_ADDED = "comment_added"
    CLOSED = "closed"
    REOPENED = "reopened"
    ESCALATED = "escalated"


class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Кто изменил
    action = Column(SQLEnum(HistoryAction), nullable=False)
    old_value = Column(Text, nullable=True)  # Старое значение
    new_value = Column(Text, nullable=True)  # Новое значение
    description = Column(Text, nullable=True)  # Описание изменения
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="history")
    user = relationship("User", back_populates="ticket_history")

