"""
Template model - шаблоны ответов для операторов
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)  # Название шаблона
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)  # Категория (опционально)
    content = Column(Text, nullable=False)  # Содержимое шаблона
    is_active = Column(Boolean, default=True)  # Активен ли шаблон
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Кто создал
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="templates")
    creator = relationship("User", back_populates="templates")

