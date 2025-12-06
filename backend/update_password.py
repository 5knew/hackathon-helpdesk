"""
Скрипт для обновления пароля существующего пользователя
НЕ создает новых пользователей!
"""
import sys
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User
import hashlib

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=" * 60)
    print("Обновление пароля пользователя")
    print("=" * 60)
    
    # Обновляем пароль для ibragim@gmail.com
    user_email = "ibragim@gmail.com"
    user = db.query(User).filter(User.email == user_email).first()
    
    if user:
        # Обновляем пароль на "admin"
        user.password_hash = hash_password("admin")
        db.commit()
        print(f"[OK] Password updated for: {user_email}")
        print(f"     New password: admin")
    else:
        print(f"[ERROR] User {user_email} not found in database!")
        print("\nAll users in database:")
        all_users = db.query(User).all()
        for u in all_users:
            print(f"  - {u.email} ({u.name})")
        sys.exit(1)
    
    # Показываем всех пользователей
    print("\n" + "=" * 60)
    print("Все пользователи в базе:")
    print("=" * 60)
    all_users = db.query(User).all()
    for u in all_users:
        print(f"  - {u.email} ({u.name}) - Role: {u.role}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Password updated!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
    sys.exit(1)
finally:
    db.close()

