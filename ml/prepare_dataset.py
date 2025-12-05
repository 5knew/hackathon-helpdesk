"""
Скрипт для подготовки датасета:
1. Анализ уникальных значений
2. Создание словарей для перемаппинга
3. Применение перемаппинга
4. Добавление поля problem_type
"""

import csv
import json
from collections import Counter

# Загрузка датасета
def load_dataset(filepath):
    """Загружает датасет из CSV файла"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

# Анализ уникальных значений
def analyze_dataset(data):
    """Анализирует уникальные значения в датасете"""
    types = Counter()
    queues = Counter()
    priorities = Counter()
    languages = Counter()
    
    for row in data:
        if row.get('type'):
            types[row['type']] += 1
        if row.get('queue'):
            queues[row['queue']] += 1
        if row.get('priority'):
            priorities[row['priority']] += 1
        if row.get('language'):
            languages[row['language']] += 1
    
    return {
        'types': dict(types),
        'queues': dict(queues),
        'priorities': dict(priorities),
        'languages': dict(languages)
    }

# Словари для перемаппинга
mapping_category = {
    # TYPE -> Категория
    "Incident": "Инцидент",
    "Problem": "Проблема",
    "Request": "Запрос",
    "Change": "Изменение",
    
    # QUEUE -> Категория (дополнительная категоризация)
    "Technical Support": "Техническая поддержка",
    "IT Support": "IT поддержка",
    "Product Support": "Поддержка продукта",
    "Billing and Payments": "Биллинг и платежи",
    "Customer Service": "Клиентский сервис",
    "Sales and Pre-Sales": "Продажи",
    "Returns and Exchanges": "Возвраты и обмены",
    "Service Outages and Maintenance": "Сбои и обслуживание",
    "Human Resources": "HR",
    "General Inquiry": "Общие вопросы"
}

mapping_priority = {
    "high": "Высокий",
    "medium": "Средний",
    "low": "Низкий"
}

# Типовые категории (для определения problem_type)
typical_categories = [
    "Биллинг и платежи",
    "Клиентский сервис",
    "Общие вопросы"
]

def apply_mapping(data):
    """Применяет перемаппинг к данным"""
    result = []
    
    for row in data:
        new_row = row.copy()
        
        # Перемаппинг категории (используем queue как основную категорию)
        original_queue = row.get('queue', '')
        if original_queue in mapping_category:
            new_row['category'] = mapping_category[original_queue]
        else:
            new_row['category'] = original_queue  # Оставляем оригинальное значение, если нет маппинга
        
        # Перемаппинг приоритета
        original_priority = row.get('priority', '').lower()
        if original_priority in mapping_priority:
            new_row['priority'] = mapping_priority[original_priority]
        else:
            new_row['priority'] = original_priority
        
        # Добавление поля problem_type
        category = new_row.get('category', '')
        if category in typical_categories:
            new_row['problem_type'] = "Типовой"
        else:
            new_row['problem_type'] = "Сложный"
        
        result.append(new_row)
    
    return result

def save_dataset(data, output_filepath):
    """Сохраняет обработанный датасет в CSV"""
    if not data:
        return
    
    fieldnames = list(data[0].keys())
    
    with open(output_filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main():
    input_file = "datasets/aa_dataset-tickets-multi-lang-5-2-50-version.csv"
    output_file = "datasets/dataset_preprocessed.csv"
    
    print("=" * 60)
    print("ПОДГОТОВКА ДАТАСЕТА")
    print("=" * 60)
    
    # Загрузка данных
    print("\n1. Загрузка датасета...")
    data = load_dataset(input_file)
    print(f"   Загружено строк: {len(data)}")
    
    # Анализ
    print("\n2. Анализ уникальных значений...")
    analysis = analyze_dataset(data)
    
    print("\n   TYPE (Категория):")
    for key, count in sorted(analysis['types'].items()):
        print(f"     {key}: {count}")
    
    print("\n   QUEUE (Очередь/Отдел):")
    for key, count in sorted(analysis['queues'].items()):
        print(f"     {key}: {count}")
    
    print("\n   PRIORITY (Приоритет):")
    for key, count in sorted(analysis['priorities'].items()):
        print(f"     {key}: {count}")
    
    print("\n   LANGUAGE:")
    for key, count in sorted(analysis['languages'].items()):
        print(f"     {key}: {count}")
    
    # Применение перемаппинга
    print("\n3. Применение перемаппинга...")
    processed_data = apply_mapping(data)
    
    # Проверка результатов
    print("\n4. Проверка результатов перемаппинга...")
    categories = Counter([row.get('category', '') for row in processed_data])
    priorities = Counter([row.get('priority', '') for row in processed_data])
    problem_types = Counter([row.get('problem_type', '') for row in processed_data])
    
    print("\n   Новые категории:")
    for key, count in sorted(categories.items()):
        print(f"     {key}: {count}")
    
    print("\n   Новые приоритеты:")
    for key, count in sorted(priorities.items()):
        print(f"     {key}: {count}")
    
    print("\n   Типы проблем:")
    for key, count in sorted(problem_types.items()):
        print(f"     {key}: {count}")
    
    # Сохранение
    print(f"\n5. Сохранение обработанного датасета в {output_file}...")
    save_dataset(processed_data, output_file)
    print("   Готово!")
    
    # Сохранение словарей маппинга
    print("\n6. Сохранение словарей маппинга...")
    mappings = {
        'mapping_category': mapping_category,
        'mapping_priority': mapping_priority,
        'typical_categories': typical_categories
    }
    
    with open('mappings.json', 'w', encoding='utf-8') as f:
        json.dump(mappings, f, ensure_ascii=False, indent=2)
    print("   Сохранено в mappings.json")
    
    print("\n" + "=" * 60)
    print("ГОТОВО!")
    print("=" * 60)

if __name__ == "__main__":
    main()

