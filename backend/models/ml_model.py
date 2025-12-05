"""
ML Model model - модели ИИ и их версии
"""
from sqlalchemy import Column, String, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base


class MLModel(Base):
    __tablename__ = "ml_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # Например, "classifier_v2.3"
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=True)  # Точность модели
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = relationship("AIPrediction", back_populates="model")

