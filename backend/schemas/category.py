"""
Pydantic schemas for Category
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class CategoryCreate(BaseModel):
    """Схема для создания категории"""
    name: str
    description: Optional[str] = None
    sla_minutes: Optional[int] = None


class CategoryResponse(BaseModel):
    """Схема ответа с категорией"""
    id: UUID
    name: str
    description: Optional[str]
    sla_minutes: Optional[int]
    
    class Config:
        from_attributes = True

