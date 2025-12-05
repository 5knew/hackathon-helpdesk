"""
Ticket model - основная сущность системы
"""
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from database import Base


class TicketSource(str, enum.Enum):
    """Источники обращения"""
    EMAIL = "email"
    CHAT = "chat"
    PORTAL = "portal"
    PHONE = "phone"


class TicketLanguage(str, enum.Enum):
    """Языки"""
    RU = "ru"
    KK = "kk"
    EN = "en"


class TicketPriority(str, enum.Enum):
    """Приоритеты"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, enum.Enum):
    """Типы проблем"""
    SIMPLE = "simple"
    COMPLEX = "complex"
    AUTO_RESOLVABLE = "auto_resolvable"


class TicketStatus(str, enum.Enum):
    """Статусы тикетов"""
    NEW = "new"
    AUTO_RESOLVED = "auto_resolved"
    IN_WORK = "in_work"
    WAITING = "waiting"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(SQLEnum(TicketSource), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    language = Column(SQLEnum(TicketLanguage), default=TicketLanguage.RU)
    
    # AI классификация
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    priority = Column(SQLEnum(TicketPriority), nullable=True)
    issue_type = Column(SQLEnum(IssueType), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    
    # Маршрутизация
    assigned_department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    assigned_operator_id = Column(UUID(as_uuid=True), ForeignKey("operators.id"), nullable=True)
    
    # Статус
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.NEW)
    auto_resolved = Column(Boolean, default=False)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    category = relationship("Category", back_populates="tickets")
    department = relationship("Department", back_populates="tickets")
    operator = relationship("Operator", back_populates="assigned_tickets")
    predictions = relationship("AIPrediction", back_populates="ticket", cascade="all, delete-orphan")
    auto_responses = relationship("AIAutoResponse", back_populates="ticket", cascade="all, delete-orphan")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

