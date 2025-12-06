"""
Скрипт для создания базы данных PostgreSQL
"""
import os
import sys

# Устанавливаем кодировку UTF-8 для вывода
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("psycopg2 не установлен. Установите: pip install psycopg2-binary")
    sys.exit(1)

def create_database():
    """Создает базу данных helpdesk_db если её нет"""
    # Пробуем разные варианты подключения
    passwords = ["postgres", os.getenv("POSTGRES_PASSWORD", "")]
    users = ["postgres", os.getenv("POSTGRES_USER", "postgres")]
    
    for user in users:
        for password in passwords:
            if not password:
                continue
            try:
                # Подключаемся к базе данных postgres (по умолчанию)
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    user=user,
                    password=password,
                    database="postgres",
                    connect_timeout=5
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                
                # Проверяем, существует ли база данных
                cursor.execute("SELECT 1 FROM pg_database WHERE datname='helpdesk_db'")
                exists = cursor.fetchone()
                
                if not exists:
                    print("Creating database helpdesk_db...")
                    cursor.execute('CREATE DATABASE helpdesk_db')
                    print("Database helpdesk_db created successfully!")
                else:
                    print("Database helpdesk_db already exists")
                
                cursor.close()
                conn.close()
                return True
                
            except psycopg2.OperationalError as e:
                # Пробуем следующий вариант
                continue
            except psycopg2.Error as e:
                print(f"Error: {e}")
                return False
    
    print("Could not connect to PostgreSQL. Please check:")
    print("1. PostgreSQL is running")
    print("2. Username and password are correct")
    print("3. PostgreSQL accepts connections from localhost")
    return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)

