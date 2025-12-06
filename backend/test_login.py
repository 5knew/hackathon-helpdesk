"""
Тест входа пользователя
"""
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    email = "ibragim@gmail.com"
    password = "admin?"
    
    print("=" * 60)
    print("Testing login for:", email)
    print("=" * 60)
    
    # Ищем пользователя
    user = db.query(User).filter(User.email.ilike(email)).first()
    
    if not user:
        print(f"[ERROR] User not found!")
        print("\nAll users in database:")
        all_users = db.query(User).all()
        for u in all_users:
            print(f"  - '{u.email}' (ID: {u.id})")
    else:
        print(f"[OK] User found:")
        print(f"  Email: '{user.email}'")
        print(f"  Name: '{user.name}'")
        print(f"  Has password hash: {user.password_hash is not None}")
        
        if user.password_hash:
            # Проверяем пароль
            password_hash = hash_password(password)
            print(f"\n  Stored hash: {user.password_hash[:20]}...")
            print(f"  Computed hash: {password_hash[:20]}...")
            
            if user.password_hash == password_hash:
                print(f"\n[SUCCESS] Password matches!")
            else:
                print(f"\n[ERROR] Password does NOT match!")
                print(f"\nTrying different passwords:")
                for pwd in ["admin?", "admin!", "admin", "password123"]:
                    if hash_password(pwd) == user.password_hash:
                        print(f"  [FOUND] Correct password is: '{pwd}'")
                        break
        else:
            print(f"\n[ERROR] User has no password hash!")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

