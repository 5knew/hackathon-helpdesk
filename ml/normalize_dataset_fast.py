"""
Быстрая версия: только нормализация БЕЗ перевода
Для быстрой обработки больших датасетов
"""

import pandas as pd
import numpy as np
from typing import Dict
import os
from collections import Counter
import hashlib

# Импортируем нормализатор из основного скрипта
from normalize_and_translate_dataset import DatasetNormalizer, create_labeling_instructions


def normalize_dataset_fast(input_file: str, output_file: str):
    """
    Быстрая нормализация БЕЗ перевода
    Только нормализация дубликатов и меток
    """
    print("=" * 60)
    print("БЫСТРАЯ НОРМАЛИЗАЦИЯ ДАТАСЕТА (БЕЗ ПЕРЕВОДА)")
    print("=" * 60)
    
    # Загрузка
    print(f"\n1. Загрузка: {input_file}")
    df = pd.read_csv(input_file)
    print(f"   Загружено строк: {len(df)}")
    
    # Нормализация
    print("\n2. Нормализация...")
    normalizer = DatasetNormalizer()
    
    # Удаление дубликатов
    df = normalizer.find_duplicates(df)
    
    # Нормализация меток
    print("\n   Нормализация меток...")
    if 'category' in df.columns:
        df['category'] = df['category'].apply(normalizer.normalize_category)
    
    if 'priority' in df.columns:
        df['priority'] = df['priority'].apply(normalizer.normalize_priority)
    
    if 'problem_type' in df.columns:
        df['problem_type'] = df.apply(
            lambda row: normalizer.normalize_problem_type(
                row.get('problem_type'), 
                row.get('priority')
            ), axis=1
        )
    elif 'priority' in df.columns:
        df['problem_type'] = df['priority'].apply(
            lambda p: 'Сложный' if 'Критический' in str(p) or 'Высокий' in str(p) else 'Типовой'
        )
    
    print(f"   ✅ Нормализовано категорий: {normalizer.normalization_stats['categories_normalized']}")
    print(f"   ✅ Нормализовано приоритетов: {normalizer.normalization_stats['priorities_normalized']}")
    print(f"   ✅ Удалено дубликатов: {normalizer.normalization_stats['duplicates_removed']}")
    
    # Сохранение инструкций
    instructions = create_labeling_instructions()
    with open('labeling_instructions.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    print("   ✅ Инструкции сохранены: labeling_instructions.md")
    
    # Сохранение
    print(f"\n3. Сохранение: {output_file}")
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Статистика
    print(f"\n✅ Готово!")
    print(f"   Исходных строк: {len(df) + normalizer.normalization_stats['duplicates_removed']}")
    print(f"   После нормализации: {len(df)}")
    print(f"   Удалено дубликатов: {normalizer.normalization_stats['duplicates_removed']}")
    
    if 'category' in df.columns:
        print("\n   Категории:")
        for cat, count in df['category'].value_counts().items():
            print(f"     {cat}: {count}")
    
    if 'priority' in df.columns:
        print("\n   Приоритеты:")
        for pri, count in df['priority'].value_counts().items():
            print(f"     {pri}: {count}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Быстрая нормализация датасета (без перевода)')
    parser.add_argument('--input', '-i', 
                       default='datasets/dataset_preprocessed.csv',
                       help='Входной файл')
    parser.add_argument('--output', '-o',
                       default='datasets/dataset_normalized.csv',
                       help='Выходной файл')
    
    args = parser.parse_args()
    
    normalize_dataset_fast(args.input, args.output)

