"""
Объединение нескольких датасетов для повышения устойчивости модели
"""

import pandas as pd
import os

def merge_datasets(dataset_paths, output_path):
    """
    Объединяет несколько датасетов в один
    
    Args:
        dataset_paths: список путей к CSV файлам
        output_path: путь для сохранения объединенного датасета
    """
    datasets = []
    
    print("=" * 60)
    print("ОБЪЕДИНЕНИЕ ДАТАСЕТОВ")
    print("=" * 60)
    
    for i, path in enumerate(dataset_paths, 1):
        if os.path.exists(path):
            print(f"\n{i}. Загрузка: {path}")
            df = pd.read_csv(path)
            print(f"   Загружено строк: {len(df)}")
            datasets.append(df)
        else:
            print(f"\n⚠️  Файл не найден: {path}")
    
    if not datasets:
        print("\n❌ Нет данных для объединения!")
        return None
    
    # Объединение датасетов
    print("\n" + "=" * 60)
    print("Объединение датасетов...")
    full_df = pd.concat(datasets, ignore_index=True)
    
    # Удаление дубликатов (если есть)
    initial_len = len(full_df)
    full_df = full_df.drop_duplicates(subset=['subject', 'body'], keep='first')
    duplicates_removed = initial_len - len(full_df)
    
    if duplicates_removed > 0:
        print(f"   Удалено дубликатов: {duplicates_removed}")
    
    # Удаление строк с пустыми значениями в ключевых полях
    full_df = full_df.dropna(subset=['text', 'category', 'priority', 'problem_type'])
    
    print(f"   Итого строк: {len(full_df)}")
    
    # Сохранение
    print(f"\nСохранение объединенного датасета в: {output_path}")
    full_df.to_csv(output_path, index=False, encoding='utf-8')
    
    # Статистика
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ОБЪЕДИНЕННОГО ДАТАСЕТА")
    print("=" * 60)
    
    print("\nРаспределение по категориям:")
    print(full_df['category'].value_counts())
    
    print("\nРаспределение по приоритетам:")
    print(full_df['priority'].value_counts())
    
    print("\nРаспределение по типам проблем:")
    print(full_df['problem_type'].value_counts())
    
    print("\n✅ Объединение завершено!")
    
    return full_df

if __name__ == "__main__":
    # Пример использования
    datasets_to_merge = [
        "datasets/dataset_mapped.csv",  # Основной обработанный датасет
        # "datasets/public_dataset_cleaned.csv",  # Публичные данные (если есть)
        # "datasets/synthetic_dataset.csv",  # Синтетические данные (если есть)
        # "datasets/your_own_tickets.csv",  # Реальные тикеты (если есть)
    ]
    
    output_file = "datasets/dataset_merged.csv"
    
    merge_datasets(datasets_to_merge, output_file)

