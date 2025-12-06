"""
Category model - категории тикетов
"""
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    sla_minutes = Column(Integer, nullable=True)  # Требуемый SLA в минутах
    
    # Relationships
    tickets = relationship("Ticket", back_populates="category")
    training_samples = relationship("TrainingSample", back_populates="category")
    templates = relationship("Template", back_populates="category")

