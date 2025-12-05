"""
Pydantic schemas for Operator
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class OperatorCreate(BaseModel):
    """Схема для создания оператора"""
    user_id: UUID
    department_id: Optional[UUID] = None
    is_active: bool = True


class OperatorResponse(BaseModel):
    """Схема ответа с оператором"""
    id: UUID
    user_id: UUID
    department_id: Optional[UUID]
    is_active: bool
    
    class Config:
        from_attributes = True

