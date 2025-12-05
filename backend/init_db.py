"""
Скрипт для инициализации базы данных PostgreSQL
Создает все таблицы и заполняет начальными данными
"""
import os
from sqlalchemy import create_engine
from database import Base, engine

# Импортируем все модели для регистрации в Base.metadata
from models.ticket import Ticket
from models.user import User
from models.department import Department
from models.operator import Operator
from models.category import Category
from models.ml_model import MLModel
from models.ai_prediction import AIPrediction
from models.ai_auto_response import AIAutoResponse
from models.ticket_message import TicketMessage
from models.daily_stat import DailyStat
from models.training_sample import TrainingSample


def init_database():
    """Создает все таблицы в БД"""
    print("Создание таблиц в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно!")


def seed_initial_data():
    """Заполняет БД начальными данными"""
    from sqlalchemy.orm import sessionmaker
    from database import engine
    
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Создаем департаменты
        departments_data = [
            {"name": "General Support", "description": "Общая поддержка"},
            {"name": "Billing", "description": "Отдел биллинга"},
            {"name": "Tech Support", "description": "Техническая поддержка"},
            {"name": "HR", "description": "Отдел кадров"},
            {"name": "Customer Service", "description": "Клиентский сервис"},
        ]
        
        for dept_data in departments_data:
            existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
            if not existing:
                dept = Department(**dept_data)
                db.add(dept)
        
        # Создаем категории
        categories_data = [
            {"name": "Общие вопросы", "description": "Общие вопросы", "sla_minutes": 1440},
            {"name": "Биллинг", "description": "Вопросы по оплате", "sla_minutes": 240},
            {"name": "Техническая поддержка", "description": "Технические проблемы", "sla_minutes": 480},
            {"name": "HR вопросы", "description": "Вопросы кадров", "sla_minutes": 1440},
            {"name": "Клиентский сервис", "description": "Сервисные вопросы", "sla_minutes": 720},
        ]
        
        for cat_data in categories_data:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(**cat_data)
                db.add(category)
        
        # Создаем дефолтную ML модель
        existing_model = db.query(MLModel).filter(MLModel.name == "default_classifier").first()
        if not existing_model:
            ml_model = MLModel(
                name="default_classifier",
                version="1.0",
                description="Default ML classifier model",
                accuracy=0.85
            )
            db.add(ml_model)
        
        db.commit()
        print("✅ Начальные данные добавлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при заполнении данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Инициализация базы данных...")
    print(f"📊 DATABASE_URL: {os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/helpdesk_db')}")
    
    init_database()
    seed_initial_data()
    
    print("\n✅ Инициализация завершена успешно!")
    print("Теперь можно запускать приложение: python run.py")

