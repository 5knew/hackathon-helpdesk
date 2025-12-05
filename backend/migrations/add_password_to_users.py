"""
Миграция: добавление поля password_hash в таблицу users
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import text
from database import engine

def migrate():
    """Добавляет поле password_hash в таблицу users"""
    with engine.connect() as conn:
        try:
            # Проверяем, существует ли колонка
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='password_hash'
            """))
            
            if result.fetchone() is None:
                # Добавляем колонку
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN password_hash VARCHAR(255)
                """))
                conn.commit()
                print("✅ Колонка password_hash добавлена в таблицу users")
            else:
                print("ℹ️ Колонка password_hash уже существует")
        except Exception as e:
            print(f"❌ Ошибка при миграции: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()

