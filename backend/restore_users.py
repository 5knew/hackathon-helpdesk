"""
Скрипт для восстановления пользователей в базе данных
"""
import sys
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User, UserRole
import hashlib

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=" * 60)
    print("Восстановление пользователей")
    print("=" * 60)
    
    # Создаем/восстанавливаем админа
    admin_email = "admin@helpdesk.com"
    admin = db.query(User).filter(User.email == admin_email).first()
    
    if not admin:
        print(f"\n[CREATING] Creating admin user: {admin_email}")
        admin = User(
            email=admin_email,
            name="Админ",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN.value
        )
        db.add(admin)
        db.commit()
        print(f"[OK] Admin user created: {admin_email} / admin123")
    else:
        # Обновляем пароль на случай, если он был изменен
        admin.password_hash = hash_password("admin123")
        admin.name = "Админ"
        admin.role = UserRole.ADMIN.value
        db.commit()
        print(f"[OK] Admin user exists: {admin_email} / admin123")
    
    # Создаем/восстанавливаем пользователя ibragim@gmail.com
    user_email = "ibragim@gmail.com"
    user = db.query(User).filter(User.email == user_email).first()
    
    if not user:
        print(f"\n[CREATING] Creating user: {user_email}")
        user = User(
            email=user_email,
            name="Ibragim",
            password_hash=hash_password("admin!"),
            role=UserRole.CLIENT.value
        )
        db.add(user)
        db.commit()
        print(f"[OK] User created: {user_email} / admin!")
    else:
        # Обновляем пароль на admin!
        user.password_hash = hash_password("admin!")
        user.name = "Ibragim"
        db.commit()
        print(f"[OK] User exists and password updated: {user_email} / admin!")
    
    # Показываем всех пользователей
    print("\n" + "=" * 60)
    print("Все пользователи в базе:")
    print("=" * 60)
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email} ({u.name}) - Role: {u.role}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Restoration completed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()

