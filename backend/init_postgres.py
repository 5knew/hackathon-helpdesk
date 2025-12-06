"""
Скрипт для инициализации PostgreSQL базы данных
Создает БД, таблицы и начальные данные (включая админа)
"""
import os
import sys

# Устанавливаем кодировку UTF-8 для Windows
if sys.platform == 'win32':
    import codecs
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        except:
            pass

print("=" * 60)
print("Инициализация PostgreSQL базы данных для Help Desk")
print("=" * 60)

# Импортируем setup_db функции
from setup_db import create_database_if_not_exists, init_tables, seed_data

def main():
    print("\nШаг 1: Создание базы данных...")
    if not create_database_if_not_exists():
        print("\n❌ Ошибка: Не удалось создать базу данных")
        print("\nПопробуйте создать базу данных вручную:")
        print("1. Откройте pgAdmin 4")
        print("2. Подключитесь к серверу PostgreSQL")
        print("3. Создайте базу данных: helpdesk_db")
        sys.exit(1)
    
    print("\nШаг 2: Создание таблиц...")
    if not init_tables():
        print("\n❌ Ошибка: Не удалось создать таблицы")
        sys.exit(1)
    
    print("\nШаг 3: Заполнение начальными данными...")
    if not seed_data():
        print("\n⚠️  Предупреждение: Не удалось заполнить начальные данные")
        print("Но таблицы созданы, можно продолжить")
    
    print("\n" + "=" * 60)
    print("✅ Инициализация завершена успешно!")
    print("=" * 60)
    print("\nСоздан администратор:")
    print("  Email: admin@helpdesk.com")
    print("  Password: admin123")
    print("\nТеперь можно запустить бэкенд: python run.py")
    print("=" * 60)

if __name__ == "__main__":
    main()


