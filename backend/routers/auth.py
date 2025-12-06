"""
Authentication router - регистрация и вход пользователей
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from database import get_db
from schemas.auth import UserRegister, UserLogin, TokenResponse
from schemas.user import UserResponse
from models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# OAuth2 схема для токенов (для будущего использования)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Простая реализация токенов (в продакшене использовать JWT)
# Храним токены в памяти (можно перенести в Redis)
active_tokens = {}


def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return hash_password(plain_password) == hashed_password


def create_access_token(user_id: str) -> str:
    """Создает токен доступа"""
    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        "user_id": user_id,
        "created_at": datetime.utcnow()
    }
    return token


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    """
    # Нормализуем email (убираем пробелы, приводим к нижнему регистру)
    normalized_email = user_data.email.strip().lower()
    
    # Проверяем, существует ли пользователь с таким email (регистронезависимый поиск)
    existing_user = db.query(User).filter(User.email.ilike(normalized_email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя (сохраняем нормализованный email)
    user = User(
        email=normalized_email,
        name=user_data.name,
        phone=user_data.phone,
        position=user_data.position,
        role=user_data.role,
        password_hash=hash_password(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Вход пользователя (получение токена)
    """
    # Логируем входящие данные для отладки
    print(f"[LOGIN] Attempt: email='{login_data.email}' (type: {type(login_data.email)}), password='{login_data.password}' (length: {len(login_data.password)})")
    
    # Нормализуем email (убираем пробелы, приводим к нижнему регистру)
    # EmailStr уже может быть нормализован, но на всякий случай делаем еще раз
    normalized_email = str(login_data.email).strip().lower()
    print(f"[LOGIN] Normalized email: '{normalized_email}'")
    
    # Находим пользователя по email (регистронезависимый поиск)
    user = db.query(User).filter(User.email.ilike(normalized_email)).first()
    
    if not user:
        print(f"[LOGIN] User not found for email: '{normalized_email}'")
        # Показываем все пользователи для отладки
        all_users = db.query(User).all()
        print(f"[LOGIN] Available users: {[u.email for u in all_users]}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    print(f"[LOGIN] User found: {user.email}, has_password: {user.password_hash is not None}")
    
    # Проверяем пароль
    password_match = verify_password(login_data.password, user.password_hash) if user.password_hash else False
    print(f"[LOGIN] Password match: {password_match}")
    
    if not user.password_hash or not password_match:
        print(f"[LOGIN] Password verification failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    print(f"[LOGIN] Login successful for: {user.email}")
    
    # Создаем токен
    access_token = create_access_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    )


@router.post("/login/form", response_model=TokenResponse)
def login_user_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Вход через OAuth2 форму (для Swagger UI)
    """
    # Нормализуем email
    normalized_email = form_data.username.strip().lower()
    
    # Находим пользователя по email (регистронезависимый поиск)
    user = db.query(User).filter(User.email.ilike(normalized_email)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    if not user.password_hash or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    access_token = create_access_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        name=user.name,
        role=user.role
    )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Получение информации о текущем пользователе
    """
    # Проверяем токен
    token_data = active_tokens.get(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )
    
    user_id = token_data["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.post("/logout")
def logout_user(token: str = Depends(oauth2_scheme)):
    """
    Выход пользователя (удаление токена)
    """
    if token in active_tokens:
        del active_tokens[token]
        return {"message": "Успешный выход"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не найден"
        )

