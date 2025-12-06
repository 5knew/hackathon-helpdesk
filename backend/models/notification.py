"""
Notification model - уведомления для пользователей
"""
from sqlalchemy import Column, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from database import Base


class NotificationType(str, enum.Enum):
    """Типы уведомлений"""
    COMMENT = "comment"  # Новый комментарий в тикете
    ADMIN_REPLY = "admin_reply"  # Админ ответил на тикет
    TICKET_CREATED = "ticket_created"  # Создан новый тикет
    TICKET_UPDATED = "ticket_updated"  # Тикет обновлен
    TICKET_CLOSED = "ticket_closed"  # Тикет закрыт
    ASSIGNED = "assigned"  # Тикет назначен оператору


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(Text, nullable=False)  # Заголовок уведомления
    message = Column(Text, nullable=False)  # Текст уведомления
    is_read = Column(Boolean, default=False, nullable=False)  # Прочитано ли уведомление
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    ticket = relationship("Ticket", back_populates="notifications")


