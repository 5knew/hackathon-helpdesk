"""
Скрипт для создания базы данных и инициализации таблиц
Обходит проблему с кодировкой в psycopg2
"""
import os
import sys

# Устанавливаем кодировку UTF-8
if sys.platform == 'win32':
    import codecs
    try:
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    except:
        pass

from sqlalchemy import create_engine, text

def create_database_if_not_exists():
    """Создает базу данных helpdesk_db если её нет"""
    # Подключаемся к базе данных postgres (по умолчанию)
    # Используем пароль из переменной окружения или дефолтный
    pg_password = os.getenv("PGPASSWORD", "admin")
    postgres_url = f"postgresql://postgres:{pg_password}@localhost:5432/postgres"
    
    try:
        engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Проверяем, существует ли база данных
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='helpdesk_db'"))
            exists = result.fetchone()
            
            if not exists:
                print("Creating database helpdesk_db...")
                conn.execute(text("CREATE DATABASE helpdesk_db"))
                print("Database helpdesk_db created successfully!")
            else:
                print("Database helpdesk_db already exists")
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        print("\nPlease create the database manually:")
        print("1. Open pgAdmin or use psql")
        print("2. Connect to PostgreSQL")
        print("3. Run: CREATE DATABASE helpdesk_db;")
        return False

def init_tables():
    """Создает таблицы в базе данных"""
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
    from models.notification import Notification
    
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def seed_data():
    """Заполняет БД начальными данными"""
    from sqlalchemy.orm import sessionmaker
    from database import engine
    from models.department import Department
    from models.category import Category
    from models.ml_model import MLModel
    from models.user import User, UserRole
    import hashlib
    
    def hash_password(password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
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
        
        # Создаем администратора по умолчанию
        admin_email = "admin@helpdesk.com"
        admin_password = "admin123"  # В продакшене использовать безопасный пароль
        admin_password_hash = hash_password(admin_password)
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin = User(
                email=admin_email,
                name="Админ",
                password_hash=admin_password_hash,
                role=UserRole.ADMIN.value
            )
            db.add(admin)
            print(f"Created admin user: {admin_email} / {admin_password}")
        else:
            # Обновляем имя админа, если оно отличается
            if existing_admin.name != "Админ":
                existing_admin.name = "Админ"
                db.commit()
                print(f"Updated admin name to 'Админ'")
        
        db.commit()
        print("Initial data seeded successfully!")
        return True
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Setting up database...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/helpdesk_db')}")
    
    # Шаг 1: Создать базу данных
    if not create_database_if_not_exists():
        sys.exit(1)
    
    # Шаг 2: Создать таблицы
    if not init_tables():
        sys.exit(1)
    
    # Шаг 3: Заполнить начальными данными
    if not seed_data():
        print("Warning: Could not seed initial data, but tables are created")
    
    print("\nDatabase setup completed successfully!")
    print("You can now run the backend: python run.py")


