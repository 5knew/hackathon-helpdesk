import pandas as pd
import json

# Загрузка датасета
df = pd.read_csv("datasets/aa_dataset-tickets-multi-lang-5-2-50-version.csv")

print("=" * 60)
print("АНАЛИЗ ДАТАСЕТА")
print("=" * 60)

# Анализ категорий (type)
print("\n=== TYPE (Категория) ===")
print(f"Уникальных значений: {df['type'].nunique()}")
print(f"Все значения:\n{df['type'].value_counts()}")
print(f"\nУникальные значения:\n{df['type'].unique()}")

# Анализ очередей (queue)
print("\n=== QUEUE (Очередь/Отдел) ===")
print(f"Уникальных значений: {df['queue'].nunique()}")
print(f"Все значения:\n{df['queue'].value_counts()}")
print(f"\nУникальные значения:\n{df['queue'].unique()}")

# Анализ приоритетов (priority)
print("\n=== PRIORITY (Приоритет) ===")
print(f"Уникальных значений: {df['priority'].nunique()}")
print(f"Все значения:\n{df['priority'].value_counts()}")
print(f"\nУникальные значения:\n{df['priority'].unique()}")

# Анализ языков
print("\n=== LANGUAGE ===")
print(f"Уникальных значений: {df['language'].nunique()}")
print(f"Все значения:\n{df['language'].value_counts()}")

# Анализ тегов
print("\n=== TAGS (Первые 3 тега) ===")
tag_columns = [col for col in df.columns if col.startswith('tag_')]
for tag_col in tag_columns[:3]:
    print(f"\n{tag_col}:")
    print(df[tag_col].value_counts().head(10))

print("\n" + "=" * 60)
print("СТРУКТУРА ДАТАСЕТА")
print("=" * 60)
print(f"Всего строк: {len(df)}")
print(f"Колонки: {list(df.columns)}")

