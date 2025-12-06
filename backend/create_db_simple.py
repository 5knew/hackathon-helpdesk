"""
Простой скрипт для создания базы данных через subprocess
"""
import subprocess
import sys
import os

psql_path = r"C:\Program Files\PostgreSQL\17\bin\psql.exe"

def create_database():
    """Создает базу данных helpdesk_db"""
    # Сначала проверяем, существует ли база данных
    check_cmd = [
        psql_path,
        "-U", "postgres",
        "-h", "localhost",
        "-d", "postgres",
        "-c", "SELECT 1 FROM pg_database WHERE datname='helpdesk_db'"
    ]
    
    try:
        result = subprocess.run(
            check_cmd,
            env={**os.environ, "PGPASSWORD": "postgres"},
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if 'helpdesk_db' in result.stdout or result.returncode != 0:
            # База данных уже существует или произошла ошибка
            if result.returncode == 0:
                print("Database helpdesk_db already exists")
                return True
    except Exception as e:
        print(f"Error checking database: {e}")
    
    # Создаем базу данных
    create_cmd = [
        psql_path,
        "-U", "postgres",
        "-h", "localhost",
        "-d", "postgres",
        "-c", "CREATE DATABASE helpdesk_db;"
    ]
    
    try:
        result = subprocess.run(
            create_cmd,
            env={**os.environ, "PGPASSWORD": "postgres"},
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("Database helpdesk_db created successfully!")
            return True
        else:
            print(f"Error creating database: {result.stderr}")
            print("\nPlease create the database manually using pgAdmin:")
            print("1. Open pgAdmin 4")
            print("2. Connect to PostgreSQL server")
            print("3. Right-click on 'Databases' -> Create -> Database")
            print("4. Name: helpdesk_db")
            print("5. Click Save")
            return False
    except FileNotFoundError:
        print(f"psql.exe not found at {psql_path}")
        print("Please create the database manually using pgAdmin")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    sys.exit(0 if success else 1)



