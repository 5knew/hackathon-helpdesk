"""
Pydantic schemas for User
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    email: EmailStr
    phone: Optional[str] = None
    name: str
    position: Optional[str] = None
    role: str = "client"


class UserResponse(BaseModel):
    """Схема ответа с пользователем"""
    id: UUID
    email: str
    phone: Optional[str]
    name: str
    position: Optional[str]
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

