"""
Улучшенный скрипт для нормализации, перевода и преобразования датасета
Согласно ТЗ:
- Нормализация дубликатов
- Четкие схемы меток (категория, приоритет, тип проблемы)
- Инструкции для разметчиков
- Перевод на RU/KZ
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Set
import os
from tqdm import tqdm
import json
from collections import Counter
import hashlib

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️  deep-translator не установлен. Установите: pip install deep-translator")


class DatasetNormalizer:
    """Класс для нормализации датасета"""
    
    # Четкие схемы меток согласно ТЗ
    CATEGORY_SCHEMA = {
        'IT поддержка': [
            'IT', 'IT Support', 'IT поддержка', 
            'Technical Support', 'Техническая поддержка',
            'Сбои и обслуживание'
        ],
        'Биллинг и платежи': [
            'Billing', 'Payment', 'Invoice', 'Биллинг', 'Платежи',
            'Billing and Payments', 'Биллинг и платежи'
        ],
        'Клиентский сервис': [
            'Customer Service', 'Support', 'Клиентский сервис',
            'Поддержка продукта', 'Product Support'
        ],
        'HR': [
            'HR', 'Human Resources', 'Кадры', 'Human Resources'
        ],
        'Общие вопросы': [
            'General', 'FAQ', 'Общие вопросы', 'Вопросы',
            'General Inquiry', 'Продажи', 'Sales',
            'Возвраты и обмены', 'Returns and Exchanges'
        ]
    }
    
    PRIORITY_SCHEMA = {
        'Критический': ['Critical', 'P1', 'Высокий', 'High', 'Критический'],
        'Высокий': ['High', 'P2', 'Средний', 'Medium', 'Высокий'],
        'Средний': ['Medium', 'P3', 'Низкий', 'Low', 'Средний'],
        'Низкий': ['Low', 'P4', 'Низкий']
    }
    
    PROBLEM_TYPE_SCHEMA = {
        'Типовой': ['Typical', 'Standard', 'FAQ', 'Common', 'Типовой', 'Обычный'],
        'Сложный': ['Complex', 'Critical', 'Urgent', 'Сложный', 'Критический']
    }
    
    def __init__(self):
        self.duplicate_cache = {}
        self.normalization_stats = {
            'duplicates_removed': 0,
            'categories_normalized': 0,
            'priorities_normalized': 0,
            'problem_types_normalized': 0
        }
    
    def normalize_category(self, category: str) -> str:
        """Нормализует категорию согласно схеме"""
        if pd.isna(category) or not category:
            return 'Общие вопросы'
        
        category_str = str(category).strip()
        original = category_str
        
        # Поиск в схеме (точное совпадение)
        for normalized, variants in self.CATEGORY_SCHEMA.items():
            if category_str == normalized:
                return normalized
            if category_str in variants:
                self.normalization_stats['categories_normalized'] += 1
                return normalized
        
        # Поиск по частичному совпадению (более гибкий)
        category_lower = category_str.lower()
        for normalized, variants in self.CATEGORY_SCHEMA.items():
            for variant in variants:
                if variant.lower() in category_lower or category_lower in variant.lower():
                    if category_str != normalized:
                        self.normalization_stats['categories_normalized'] += 1
                    return normalized
        
        # Дополнительные правила для известных категорий
        category_mapping = {
            'Поддержка продукта': 'Клиентский сервис',
            'Product Support': 'Клиентский сервис',
            'Возвраты и обмены': 'Клиентский сервис',
            'Returns and Exchanges': 'Клиентский сервис',
            'Продажи': 'Общие вопросы',
            'Sales': 'Общие вопросы',
            'Sales and Pre-Sales': 'Общие вопросы',
        }
        
        if category_str in category_mapping:
            self.normalization_stats['categories_normalized'] += 1
            return category_mapping[category_str]
        
        # Если не найдено, возвращаем как есть
        return category_str
    
    def normalize_priority(self, priority: str) -> str:
        """Нормализует приоритет согласно схеме"""
        if pd.isna(priority) or not priority:
            return 'Средний'
        
        priority_str = str(priority).strip()
        
        # Поиск в схеме
        for normalized, variants in self.PRIORITY_SCHEMA.items():
            if priority_str in variants or any(v.lower() in priority_str.lower() for v in variants):
                if priority_str != normalized:
                    self.normalization_stats['priorities_normalized'] += 1
                return normalized
        
        return priority_str
    
    def normalize_problem_type(self, problem_type: str, priority: str = None) -> str:
        """Нормализует тип проблемы согласно схеме"""
        if pd.isna(problem_type) or not problem_type:
            # Определяем по приоритету, если не указан
            if priority and 'Критический' in str(priority):
                return 'Сложный'
            return 'Типовой'
        
        problem_type_str = str(problem_type).strip()
        
        # Поиск в схеме
        for normalized, variants in self.PROBLEM_TYPE_SCHEMA.items():
            if problem_type_str in variants or any(v.lower() in problem_type_str.lower() for v in variants):
                if problem_type_str != normalized:
                    self.normalization_stats['problem_types_normalized'] += 1
                return normalized
        
        return problem_type_str
    
    def create_text_hash(self, text: str) -> str:
        """Создает хэш текста для поиска дубликатов"""
        if pd.isna(text) or not text:
            return ''
        # Нормализуем текст (убираем пробелы, приводим к нижнему регистру)
        normalized = str(text).lower().strip().replace('\n', ' ').replace('\r', ' ')
        # Убираем множественные пробелы
        normalized = ' '.join(normalized.split())
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def find_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Находит и удаляет дубликаты"""
        print("\n   Поиск дубликатов...")
        
        # Создаем хэш для subject + body
        df['text_hash'] = (df['subject'].fillna('').astype(str) + ' ' + 
                          df['body'].fillna('').astype(str)).apply(self.create_text_hash)
        
        initial_count = len(df)
        
        # Удаляем дубликаты, оставляя первую запись
        df_clean = df.drop_duplicates(subset=['text_hash'], keep='first')
        
        duplicates_removed = initial_count - len(df_clean)
        self.normalization_stats['duplicates_removed'] = duplicates_removed
        
        # Удаляем временную колонку
        if 'text_hash' in df_clean.columns:
            df_clean = df_clean.drop(columns=['text_hash'])
        
        print(f"   Удалено дубликатов: {duplicates_removed}")
        
        return df_clean


class DatasetTranslator:
    """Класс для перевода датасета"""
    
    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self.cache_file = "translation_cache.json"
        self.cache = self._load_cache() if use_cache else {}
        
        if TRANSLATOR_AVAILABLE:
            self.translator_ru = GoogleTranslator(source='auto', target='ru')
            self.translator_kz = GoogleTranslator(source='auto', target='kk')
            print("✅ Переводчик инициализирован")
        else:
            self.translator_ru = None
            self.translator_kz = None
            print("⚠️  Переводчик недоступен")
    
    def _load_cache(self) -> Dict:
        """Загружает кэш переводов"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Сохраняет кэш переводов"""
        if self.use_cache:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def translate_text(self, text: str, target_lang: str = 'ru') -> str:
        """Переводит текст на целевой язык"""
        if not text or pd.isna(text) or str(text).strip() == '':
            return ''
        
        text = str(text).strip()
        
        # Проверка кэша
        cache_key = f"{text}_{target_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Если уже на нужном языке
        if target_lang == 'ru' and self._is_russian(text):
            result = text
        elif target_lang == 'kz' and self._is_kazakh(text):
            result = text
        else:
            # Перевод
            try:
                if TRANSLATOR_AVAILABLE and self.translator_ru and self.translator_kz:
                    if target_lang == 'ru':
                        result = self.translator_ru.translate(text[:4500])  # Лимит API
                    elif target_lang == 'kz':
                        result = self.translator_kz.translate(text[:4500])
                    else:
                        result = text
                else:
                    result = text
            except Exception as e:
                print(f"⚠️  Ошибка перевода: {e}")
                result = text
        
        self.cache[cache_key] = result
        return result
    
    def _is_russian(self, text: str) -> bool:
        """Проверяет, является ли текст русским"""
        return any('\u0400' <= char <= '\u04FF' for char in text) and not self._is_kazakh(text)
    
    def _is_kazakh(self, text: str) -> bool:
        """Проверяет, является ли текст казахским"""
        kz_chars = ['ә', 'ғ', 'қ', 'ң', 'ө', 'ұ', 'ү', 'һ', 'і']
        return any(char in text.lower() for char in kz_chars)


def create_labeling_instructions() -> str:
    """Создает инструкции для разметчиков"""
    instructions = """
# ИНСТРУКЦИИ ДЛЯ РАЗМЕТЧИКОВ

## Схемы меток

### 1. КАТЕГОРИЯ (category)

Используйте ТОЛЬКО следующие категории:

- **IT поддержка** - технические проблемы, доступ к системам, настройка ПО
- **Биллинг и платежи** - вопросы по оплате, счетам, подпискам
- **Клиентский сервис** - общие вопросы клиентов, жалобы, предложения
- **HR** - вопросы по кадрам, отпускам, зарплате
- **Общие вопросы** - FAQ, общая информация, неопределенные запросы

**Правила для расплывчатых кейсов:**
- Если запрос содержит несколько тем → выбирайте наиболее критичную
- Если непонятно → используйте "Общие вопросы"
- При сомнениях → эскалируйте в "Общие вопросы" для ручной проверки

### 2. ПРИОРИТЕТ (priority)

Используйте ТОЛЬКО следующие приоритеты:

- **Критический** - система не работает, критическая ошибка, блокирует работу
- **Высокий** - серьезная проблема, влияет на работу, требует быстрого решения
- **Средний** - стандартная проблема, не блокирует работу
- **Низкий** - некритичная проблема, можно решить позже

**Правила:**
- Критический: система недоступна, потеря данных, безопасность
- Высокий: влияет на продуктивность, но есть обходной путь
- Средний: стандартные запросы, типовые проблемы
- Низкий: улучшения, вопросы, некритичные запросы

### 3. ТИП ПРОБЛЕМЫ (problem_type)

Используйте ТОЛЬКО следующие типы:

- **Типовой** - стандартная проблема, есть готовое решение, можно автоматизировать
- **Сложный** - требует экспертизы, уникальный случай, нужна ручная обработка

**Правила:**
- Типовой: FAQ, стандартные процедуры, известные решения
- Сложный: уникальные случаи, требует анализа, эскалация

## Примеры разметки

### Пример 1: Типовой запрос
- **Текст**: "Как сбросить пароль?"
- **Категория**: Общие вопросы
- **Приоритет**: Низкий
- **Тип проблемы**: Типовой

### Пример 2: Критический инцидент
- **Текст**: "Сервер не отвечает, все системы недоступны"
- **Категория**: IT поддержка
- **Приоритет**: Критический
- **Тип проблемы**: Сложный

### Пример 3: Вопрос по оплате
- **Текст**: "Когда нужно оплачивать счет?"
- **Категория**: Биллинг и платежи
- **Приоритет**: Средний
- **Тип проблемы**: Типовой

## Важные замечания

1. **Консистентность**: Всегда используйте одинаковые метки для похожих случаев
2. **При сомнениях**: Выбирайте более общую категорию и более высокий приоритет
3. **Документируйте**: Если встречаете новый тип запроса, документируйте его
4. **Проверка**: Регулярно проверяйте консистентность разметки
"""
    return instructions


def normalize_and_translate_dataset(input_file: str, output_file: str, 
                                   translate: bool = True, sample_size: int = None):
    """
    Нормализует, переводит и преобразует датасет
    
    Args:
        input_file: путь к исходному датасету
        output_file: путь для сохранения результата
        translate: переводить ли тексты
        sample_size: размер выборки для обработки
    """
    print("=" * 60)
    print("НОРМАЛИЗАЦИЯ И ПЕРЕВОД ДАТАСЕТА")
    print("=" * 60)
    
    # Загрузка датасета
    print(f"\n1. Загрузка датасета: {input_file}")
    df = pd.read_csv(input_file)
    
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=42)
        print(f"   Используется выборка: {len(df)} строк")
    else:
        print(f"   Загружено строк: {len(df)}")
    
    # Нормализация
    print("\n2. Нормализация датасета...")
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
        # Создаем problem_type на основе приоритета
        df['problem_type'] = df['priority'].apply(
            lambda p: 'Сложный' if 'Критический' in str(p) or 'Высокий' in str(p) else 'Типовой'
        )
    
    print(f"   Нормализовано категорий: {normalizer.normalization_stats['categories_normalized']}")
    print(f"   Нормализовано приоритетов: {normalizer.normalization_stats['priorities_normalized']}")
    print(f"   Нормализовано типов проблем: {normalizer.normalization_stats['problem_types_normalized']}")
    
    # Перевод
    translator = None
    if translate:
        print("\n3. Инициализация переводчика...")
        translator = DatasetTranslator()
    
    # Создание дубликатов для RU/KZ с оптимизацией
    print("\n4. Создание дубликатов для RU/KZ...")
    
    # Инициализируем text_mapping до блока условия
    text_mapping = {}  # оригинал -> {ru: переведенный, kz: переведенный}
    
    if translate and translator:
        print("   ⚠️  Перевод может занять много времени.")
        print("   💡 Рекомендация: используйте --sample для тестирования")
        print("   💡 Или используйте --no-translate для быстрой нормализации")
        
        # Собираем все уникальные тексты для перевода (оптимизация)
        print("\n   Оптимизация: сбор уникальных текстов...")
        unique_texts = set()
        
        for idx, row in df.iterrows():
            for field in ['subject', 'body', 'answer']:
                if field in row and pd.notna(row[field]):
                    text = str(row[field]).strip()
                    if text and text not in unique_texts:
                        unique_texts.add(text)
        
        print(f"   Найдено уникальных текстов: {len(unique_texts)}")
        print("   Перевод уникальных текстов (это займет время)...")
        
        # Переводим уникальные тексты батчами
        batch_size = 10
        texts_list = list(unique_texts)
        
        for i in tqdm(range(0, len(texts_list), batch_size), desc="Перевод батчами"):
            batch = texts_list[i:i+batch_size]
            for text in batch:
                if text not in text_mapping:
                    text_mapping[text] = {}
                    try:
                        # Перевод на RU
                        if len(text) <= 4500:
                            text_mapping[text]['ru'] = translator.translate_text(text, 'ru')
                        else:
                            # Для длинных текстов разбиваем
                            parts = text[:4500].split('. ')
                            text_mapping[text]['ru'] = translator.translate_text('. '.join(parts[:5]) + '.', 'ru')
                        
                        # Перевод на KZ
                        if len(text) <= 4500:
                            text_mapping[text]['kz'] = translator.translate_text(text, 'kz')
                        else:
                            parts = text[:4500].split('. ')
                            text_mapping[text]['kz'] = translator.translate_text('. '.join(parts[:5]) + '.', 'kz')
                    except Exception as e:
                        print(f"⚠️  Ошибка перевода: {e}")
                        text_mapping[text]['ru'] = text
                        text_mapping[text]['kz'] = text
        
        print("   ✅ Перевод завершен, создание дубликатов...")
    
    # Создание дубликатов с использованием кэша переводов
    new_rows = []
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Создание дубликатов"):
        for target_lang in ['ru', 'kz']:
            new_row = row.copy()
            new_row['language'] = target_lang
            
            # Применяем переводы из кэша
            if translate and translator and text_mapping:
                for field in ['subject', 'body', 'answer']:
                    if field in new_row and pd.notna(new_row[field]):
                        text = str(new_row[field]).strip()
                        if text and text in text_mapping:
                            new_row[field] = text_mapping[text].get(target_lang, text)
            elif translate and translator:
                # Fallback на старый метод (медленный)
                if 'subject' in new_row and pd.notna(new_row['subject']):
                    subject_text = str(new_row['subject']).strip()
                    if subject_text:
                        new_row['subject'] = translator.translate_text(subject_text, target_lang)
                
                if 'body' in new_row and pd.notna(new_row['body']):
                    body = str(new_row['body']).strip()
                    if body and len(body) <= 4000:
                        new_row['body'] = translator.translate_text(body, target_lang)
            
            new_rows.append(new_row)
    
    # Создание нового датасета
    print("\n5. Создание нового датасета...")
    new_df = pd.DataFrame(new_rows)
    
    # Сохранение кэша
    if translator and translator.use_cache:
        translator._save_cache()
    
    # Сохранение инструкций
    instructions = create_labeling_instructions()
    with open('labeling_instructions.md', 'w', encoding='utf-8') as f:
        f.write(instructions)
    print("   ✅ Инструкции для разметчиков сохранены: labeling_instructions.md")
    
    # Сохранение датасета
    print(f"\n6. Сохранение в: {output_file}")
    new_df.to_csv(output_file, index=False, encoding='utf-8')
    
    # Статистика
    print(f"\n✅ Готово!")
    print(f"   Исходных строк: {len(df)}")
    print(f"   Новых строк: {len(new_df)}")
    print(f"   Удалено дубликатов: {normalizer.normalization_stats['duplicates_removed']}")
    print(f"   Увеличение: {len(new_df) / len(df):.1f}x")
    
    print("\n7. Статистика по языкам:")
    lang_counts = new_df['language'].value_counts()
    for lang, count in lang_counts.items():
        print(f"   {lang}: {count}")
    
    print("\n8. Статистика по категориям:")
    if 'category' in new_df.columns:
        cat_counts = new_df['category'].value_counts()
        for cat, count in cat_counts.items():
            print(f"   {cat}: {count}")
    
    print("\n9. Статистика по приоритетам:")
    if 'priority' in new_df.columns:
        pri_counts = new_df['priority'].value_counts()
        for pri, count in pri_counts.items():
            print(f"   {pri}: {count}")


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Нормализация и перевод датасета')
    parser.add_argument('--input', '-i', 
                       default='datasets/dataset_preprocessed.csv',
                       help='Входной файл')
    parser.add_argument('--output', '-o',
                       default='datasets/dataset_normalized_translated.csv',
                       help='Выходной файл')
    parser.add_argument('--no-translate', action='store_true',
                       help='Не переводить, только нормализовать')
    parser.add_argument('--sample', '-s', type=int,
                       help='Обработать только N строк')
    
    args = parser.parse_args()
    
    normalize_and_translate_dataset(
        input_file=args.input,
        output_file=args.output,
        translate=not args.no_translate,
        sample_size=args.sample
    )


if __name__ == "__main__":
    main()

