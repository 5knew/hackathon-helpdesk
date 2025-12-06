"""
Скрипт для проверки и исправления базы данных
"""
import sys
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User, UserRole
from routers.auth import hash_password

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=" * 60)
    print("Проверка базы данных")
    print("=" * 60)
    
    # Проверяем админа
    admin = db.query(User).filter(User.email == "admin@helpdesk.com").first()
    
    if not admin:
        print("\n[ERROR] Administrator not found! Creating...")
        admin = User(
            email="admin@helpdesk.com",
            name="Админ",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN.value
        )
        db.add(admin)
        db.commit()
        print("[OK] Administrator created!")
    else:
        print(f"\n[OK] Administrator found:")
        print(f"   Email: {admin.email}")
        print(f"   Name: {admin.name}")
        print(f"   Role: {admin.role}")
        print(f"   Has password: {admin.password_hash is not None}")
        
        # Проверяем и обновляем имя
        if admin.name != "Админ":
            print(f"\n[WARNING] Administrator name is '{admin.name}'. Updating to 'Админ'...")
            admin.name = "Админ"
            db.commit()
            print("[OK] Administrator name updated!")
        
        # Проверяем пароль
        if not admin.password_hash or admin.password_hash != hash_password("admin123"):
            print("\n[WARNING] Administrator password is incorrect or missing. Fixing...")
            admin.password_hash = hash_password("admin123")
            db.commit()
            print("[OK] Administrator password updated!")
        
        # Проверяем роль
        if admin.role != UserRole.ADMIN.value:
            print(f"\n[WARNING] Administrator role is incorrect ({admin.role}). Fixing...")
            admin.role = UserRole.ADMIN.value
            db.commit()
            print("[OK] Administrator role updated!")
    
    # Проверяем количество пользователей
    user_count = db.query(User).count()
    print(f"\n[INFO] Total users in database: {user_count}")
    
    # Проверяем таблицы
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n[INFO] Tables in database ({len(tables)}):")
    for table in sorted(tables):
        print(f"   - {table}")
    
    # Проверяем наличие таблицы notifications
    if 'notifications' in tables:
        from models.notification import Notification
        notification_count = db.query(Notification).count()
        print(f"\n[INFO] Notifications in database: {notification_count}")
    else:
        print("\n[WARNING] Table 'notifications' not found!")
    
    print("\n" + "=" * 60)
    print("[OK] Check completed!")
    print("=" * 60)
    print("\nAdministrator credentials:")
    print("  Email: admin@helpdesk.com")
    print("  Password: admin123")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

