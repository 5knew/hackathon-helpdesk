"""
Проверка пользователя в базе данных
"""
from sqlalchemy.orm import sessionmaker
from database import engine
from models.user import User

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    email = "ibragim@gmail.com"
    
    # Проверяем точное совпадение
    user = db.query(User).filter(User.email == email).first()
    print(f"User with email '{email}':")
    if user:
        print(f"  Found: YES")
        print(f"  ID: {user.id}")
        print(f"  Email: '{user.email}'")
        print(f"  Name: '{user.name}'")
        print(f"  Has password: {user.password_hash is not None}")
        print(f"  Role: {user.role}")
    else:
        print(f"  Found: NO")
    
    # Проверяем все похожие email
    print(f"\nAll users with similar email:")
    all_users = db.query(User).all()
    for u in all_users:
        if 'ibragim' in u.email.lower() or 'gmail' in u.email.lower():
            print(f"  - '{u.email}' (ID: {u.id}, Name: {u.name})")
    
    # Проверяем регистронезависимый поиск
    print(f"\nCase-insensitive search:")
    user_ci = db.query(User).filter(User.email.ilike(email)).first()
    if user_ci:
        print(f"  Found with ilike: YES - '{user_ci.email}'")
    else:
        print(f"  Found with ilike: NO")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

