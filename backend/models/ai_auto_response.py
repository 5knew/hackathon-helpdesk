"""
AI Auto Response model - автоматические решения ИИ
"""
from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base


class AIAutoResponse(Base):
    __tablename__ = "ai_auto_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    response_text = Column(Text, nullable=False)
    is_successful = Column(Boolean, default=True)  # Успешно ли решена проблема
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="auto_responses")

