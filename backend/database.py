"""
Database configuration and connection setup for PostgreSQL
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Устанавливаем кодировку для Windows
if sys.platform == 'win32':
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    # Пробуем установить кодировку для psycopg2
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        pass

# Загружаем переменные окружения из .env файла (если есть)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не установлен, используем системные переменные

# PostgreSQL connection string
# Можно использовать переменные окружения для гибкости
# Используем PostgreSQL по умолчанию
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    # Используем SQLite для тестирования
    DATABASE_URL = "sqlite:///./helpdesk.db"
    print("⚠️  Using SQLite database (for testing). Set USE_SQLITE=false to use PostgreSQL.")
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin@localhost:5432/helpdesk_db"
    )

# Создаем engine с дополнительными параметрами для обхода проблем с кодировкой
if USE_SQLITE:
    # SQLite не требует дополнительных параметров
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Для SQLite
    )
else:
    # PostgreSQL с параметрами для обхода проблем с кодировкой
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Проверка соединения перед использованием
        pool_size=10,
        max_overflow=20,
        connect_args={
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8"
        }
    )

# Создаем SessionLocal класс
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency для получения сессии БД в FastAPI endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

