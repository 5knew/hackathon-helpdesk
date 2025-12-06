"""
Миграция для добавления новых таблиц: feedback, ticket_history, templates
"""
import os
import sys
from sqlalchemy import create_engine, text
from database import Base, engine
from models.feedback import Feedback
from models.ticket_history import TicketHistory
from models.template import Template

# Импортируем все модели для создания таблиц
from models import (
    Ticket, User, Department, Operator, Category,
    MLModel, AIPrediction, AIAutoResponse, TicketMessage,
    DailyStat, TrainingSample, Notification, Feedback,
    TicketHistory, Template
)

def migrate():
    """Создает новые таблицы в базе данных"""
    print("Starting database migration...")
    
    try:
        # Создаем все таблицы
        print("Creating tables: feedback, ticket_history, templates...")
        Base.metadata.create_all(bind=engine)
        
        # Проверяем, что таблицы созданы
        with engine.connect() as conn:
            # Проверяем feedback
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'feedback'
                );
            """))
            feedback_exists = result.scalar()
            
            # Проверяем ticket_history
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'ticket_history'
                );
            """))
            history_exists = result.scalar()
            
            # Проверяем templates
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'templates'
                );
            """))
            templates_exists = result.scalar()
            
            print(f"[OK] feedback: {'created' if feedback_exists else 'NOT created'}")
            print(f"[OK] ticket_history: {'created' if history_exists else 'NOT created'}")
            print(f"[OK] templates: {'created' if templates_exists else 'NOT created'}")
        
        # Добавляем колонки в существующую таблицу tickets
        print("Adding columns to tickets table (sla_deadline, is_escalated)...")
        with engine.connect() as conn:
            try:
                # Проверяем, существует ли колонка sla_deadline
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='tickets' AND column_name='sla_deadline';
                """))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN sla_deadline TIMESTAMP;"))
                    conn.commit()
                    print("  [OK] Added column sla_deadline")
                else:
                    print("  [INFO] Column sla_deadline already exists")
                
                # Проверяем, существует ли колонка is_escalated
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='tickets' AND column_name='is_escalated';
                """))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE tickets ADD COLUMN is_escalated BOOLEAN DEFAULT FALSE;"))
                    conn.commit()
                    print("  [OK] Added column is_escalated")
                else:
                    print("  [INFO] Column is_escalated already exists")
            except Exception as e:
                print(f"  [WARNING] Error adding columns: {e}")
                # Пробуем откатить транзакцию
                try:
                    conn.rollback()
                except:
                    pass
        
        print("\n[SUCCESS] Migration completed successfully!")
        
    except Exception as e:
        print(f"\n[ERROR] Migration error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    migrate()

