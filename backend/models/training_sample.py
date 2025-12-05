"""
Training Sample model - размеченные данные для обучения ML
"""
from sqlalchemy import Column, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base
from models.ticket import TicketPriority, IssueType


class TrainingSample(Base):
    __tablename__ = "training_samples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_text = Column(Text, nullable=False)
    true_category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    true_priority = Column(SQLEnum(TicketPriority), nullable=False)
    true_issue_type = Column(SQLEnum(IssueType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="training_samples")

