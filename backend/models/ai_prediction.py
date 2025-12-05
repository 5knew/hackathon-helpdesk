"""
AI Prediction model - предсказания ИИ по тикету
"""
from sqlalchemy import Column, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base
from models.ticket import TicketPriority, IssueType


class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=False)
    
    # Предсказания
    predicted_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    predicted_priority = Column(SQLEnum(TicketPriority), nullable=True)
    predicted_issue_type = Column(SQLEnum(IssueType), nullable=True)
    confidence = Column(Float, nullable=False)  # Общая уверенность
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")
    predicted_category = relationship("Category")

