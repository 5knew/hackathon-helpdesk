"""
Pydantic schemas for Department
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class DepartmentCreate(BaseModel):
    """Схема для создания департамента"""
    name: str
    description: Optional[str] = None


class DepartmentResponse(BaseModel):
    """Схема ответа с департаментом"""
    id: UUID
    name: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

