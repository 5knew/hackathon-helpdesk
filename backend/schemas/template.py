"""
Template schemas - схемы для шаблонов ответов
"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class TemplateCreate(BaseModel):
    """Схема для создания шаблона"""
    name: str = Field(..., min_length=1, max_length=255)
    category_id: Optional[str] = None
    content: str = Field(..., min_length=1)


class TemplateUpdate(BaseModel):
    """Схема для обновления шаблона"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category_id: Optional[str] = None
    content: Optional[str] = Field(None, min_length=1)
    is_active: Optional[bool] = None


class TemplateResponse(BaseModel):
    """Схема ответа с шаблоном"""
    id: str
    name: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None  # Название категории
    content: str
    is_active: bool
    created_by: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

