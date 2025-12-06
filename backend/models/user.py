"""
User model - клиенты и сотрудники
"""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    CLIENT = "client"
    EMPLOYEE = "employee"
    ADMIN = "admin"  # Администратор системы


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Хеш пароля
    position = Column(String(255), nullable=True)  # Должность (если сотрудник)
    role = Column(String(20), default=UserRole.CLIENT.value)  # client или employee
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="user")
    sent_messages = relationship("TicketMessage", foreign_keys="TicketMessage.sender_id", back_populates="sender")
    notifications = relationship("Notification", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
    ticket_history = relationship("TicketHistory", back_populates="user")
    templates = relationship("Template", back_populates="creator")

