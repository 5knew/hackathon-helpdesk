"""
Пример использования pandas для перемаппинга датасета
(как в инструкции пользователя)
"""

import pandas as pd

# Загрузка датасета
df = pd.read_csv("datasets/aa_dataset-tickets-multi-lang-5-2-50-version.csv")

print("=" * 60)
print("АНАЛИЗ И ПЕРЕМАППИНГ ДАТАСЕТА")
print("=" * 60)

# Посмотреть уникальные значения
print("\n=== Оригинальные категории (queue) ===")
print(df["queue"].unique())
print(f"\nРаспределение:")
print(df["queue"].value_counts())

print("\n=== Оригинальные приоритеты ===")
print(df["priority"].unique())
print(f"\nРаспределение:")
print(df["priority"].value_counts())

# Преобразовать в свои категории
mapping_category = {
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

df["category"] = df["queue"].map(mapping_category)

# Преобразовать приоритеты
mapping_priority = {
    "high": "Высокий",
    "low": "Низкий",
    "medium": "Средний"
}

df["priority"] = df["priority"].map(mapping_priority)

# Добавить поле "тип проблемы"
# Типовые категории (простые, которые можно автоматически решить)
typical_categories = [
    "Биллинг и платежи",
    "Клиентский сервис",
    "Общие вопросы"
]

df["problem_type"] = df["category"].apply(
    lambda x: "Типовой" if x in typical_categories else "Сложный"
)

# Проверка результатов
print("\n=== Результаты перемаппинга ===")
print("\nНовые категории:")
print(df["category"].value_counts())

print("\nНовые приоритеты:")
print(df["priority"].value_counts())

print("\nТипы проблем:")
print(df["problem_type"].value_counts())

# Сохранение обработанного датасета
output_file = "datasets/dataset_mapped.csv"
df.to_csv(output_file, index=False, encoding='utf-8')
print(f"\n✅ Обработанный датасет сохранен в: {output_file}")

# Показать примеры
print("\n=== Примеры обработанных данных ===")
print(df[["subject", "queue", "category", "priority", "problem_type"]].head(10))

