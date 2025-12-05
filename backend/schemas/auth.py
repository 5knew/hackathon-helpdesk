"""
Pydantic schemas for Authentication
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    position: Optional[str] = None
    role: str = "client"


class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    name: str
    role: str

