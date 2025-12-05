"""
Скрипт для перевода и преобразования датасета
Переводит все тексты на русский и казахский языки
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import os
from tqdm import tqdm
import json

# Попытка использовать библиотеку для перевода
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️  googletrans не установлен. Установите: pip install googletrans==4.0.0rc1")
    print("   Или используйте упрощенный режим без перевода")

try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False


class DatasetTranslator:
    """Класс для перевода датасета"""
    
    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self.cache_file = "translation_cache.json"
        self.cache = self._load_cache() if use_cache else {}
        
        # Инициализация переводчика
        if DEEP_TRANSLATOR_AVAILABLE:
            self.translator_ru = GoogleTranslator(source='auto', target='ru')
            self.translator_kz = GoogleTranslator(source='auto', target='kk')  # kk = казахский
            print("✅ Используется deep-translator")
        elif TRANSLATOR_AVAILABLE:
            self.translator = Translator()
            print("✅ Используется googletrans")
        else:
            self.translator = None
            print("⚠️  Переводчик недоступен, будет использован упрощенный режим")
    
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
        """
        Переводит текст на целевой язык
        
        Args:
            text: исходный текст
            target_lang: 'ru' или 'kz'
        
        Returns:
            переведенный текст
        """
        if not text or pd.isna(text) or str(text).strip() == '':
            return ''
        
        text = str(text).strip()
        
        # Проверка кэша
        cache_key = f"{text}_{target_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Если текст уже на нужном языке, возвращаем как есть
        if target_lang == 'ru' and self._is_russian(text):
            result = text
        elif target_lang == 'kz' and self._is_kazakh(text):
            result = text
        else:
            # Перевод
            try:
                if DEEP_TRANSLATOR_AVAILABLE:
                    if target_lang == 'ru':
                        result = self.translator_ru.translate(text)
                    else:
                        result = self.translator_kz.translate(text)
                elif TRANSLATOR_AVAILABLE:
                    lang_code = 'ru' if target_lang == 'ru' else 'kk'
                    result = self.translator.translate(text, dest=lang_code).text
                else:
                    # Упрощенный режим - возвращаем оригинал
                    result = text
            except Exception as e:
                print(f"⚠️  Ошибка перевода: {e}")
                result = text
        
        # Сохранение в кэш
        self.cache[cache_key] = result
        return result
    
    def _is_russian(self, text: str) -> bool:
        """Проверяет, является ли текст русским"""
        # Простая проверка по наличию кириллицы
        return any('\u0400' <= char <= '\u04FF' for char in text) and not self._is_kazakh(text)
    
    def _is_kazakh(self, text: str) -> bool:
        """Проверяет, является ли текст казахским"""
        kz_chars = ['ә', 'ғ', 'қ', 'ң', 'ө', 'ұ', 'ү', 'һ', 'і']
        return any(char in text.lower() for char in kz_chars)


def transform_dataset(input_file: str, output_file: str, translate: bool = True, 
                     sample_size: int = None):
    """
    Преобразует датасет: переводит на RU/KZ и создает дубликаты
    
    Args:
        input_file: путь к исходному датасету
        output_file: путь для сохранения результата
        translate: переводить ли тексты
        sample_size: размер выборки для обработки (None = все)
    """
    print("=" * 60)
    print("ПЕРЕВОД И ПРЕОБРАЗОВАНИЕ ДАТАСЕТА")
    print("=" * 60)
    
    # Загрузка датасета
    print(f"\n1. Загрузка датасета: {input_file}")
    df = pd.read_csv(input_file)
    
    if sample_size:
        df = df.sample(n=min(sample_size, len(df)), random_state=42)
        print(f"   Используется выборка: {len(df)} строк")
    else:
        print(f"   Загружено строк: {len(df)}")
    
    # Инициализация переводчика
    translator = None
    if translate:
        translator = DatasetTranslator()
    
    # Создание списка для новых строк
    new_rows = []
    
    print("\n2. Обработка данных...")
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Обработка"):
        # Оригинальная строка (если уже RU/KZ, оставляем как есть)
        original_lang = str(row.get('language', '')).lower()
        
        # Создаем строки для RU и KZ
        for target_lang in ['ru', 'kz']:
            new_row = row.copy()
            new_row['language'] = target_lang
            
            # Переводим subject и body
            if translate and translator:
                if 'subject' in new_row and pd.notna(new_row['subject']):
                    new_row['subject'] = translator.translate_text(new_row['subject'], target_lang)
                
                if 'body' in new_row and pd.notna(new_row['body']):
                    # Разбиваем на части для длинных текстов
                    body = str(new_row['body'])
                    if len(body) > 5000:
                        # Разбиваем на предложения
                        parts = body.split('. ')
                        translated_parts = []
                        for part in parts:
                            if part.strip():
                                translated_parts.append(translator.translate_text(part, target_lang))
                        new_row['body'] = '. '.join(translated_parts)
                    else:
                        new_row['body'] = translator.translate_text(body, target_lang)
                
                # Переводим answer, если есть
                if 'answer' in new_row and pd.notna(new_row['answer']):
                    answer = str(new_row['answer'])
                    if len(answer) > 5000:
                        parts = answer.split('. ')
                        translated_parts = []
                        for part in parts:
                            if part.strip():
                                translated_parts.append(translator.translate_text(part, target_lang))
                        new_row['answer'] = '. '.join(translated_parts)
                    else:
                        new_row['answer'] = translator.translate_text(answer, target_lang)
            
            new_rows.append(new_row)
    
    # Создание нового датасета
    print("\n3. Создание нового датасета...")
    new_df = pd.DataFrame(new_rows)
    
    # Сохранение кэша
    if translator and translator.use_cache:
        translator._save_cache()
        print(f"   Кэш сохранен: {translator.cache_file}")
    
    # Сохранение
    print(f"\n4. Сохранение в: {output_file}")
    new_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ Готово!")
    print(f"   Исходных строк: {len(df)}")
    print(f"   Новых строк: {len(new_df)}")
    print(f"   Увеличение: {len(new_df) / len(df):.1f}x")
    
    # Статистика по языкам
    print("\n5. Статистика по языкам:")
    lang_counts = new_df['language'].value_counts()
    for lang, count in lang_counts.items():
        print(f"   {lang}: {count}")


def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Перевод и преобразование датасета')
    parser.add_argument('--input', '-i', 
                       default='datasets/aa_dataset-tickets-multi-lang-5-2-50-version.csv',
                       help='Входной файл')
    parser.add_argument('--output', '-o',
                       default='datasets/dataset_translated_ru_kz.csv',
                       help='Выходной файл')
    parser.add_argument('--no-translate', action='store_true',
                       help='Не переводить, только дублировать строки')
    parser.add_argument('--sample', '-s', type=int,
                       help='Обработать только N строк (для тестирования)')
    
    args = parser.parse_args()
    
    transform_dataset(
        input_file=args.input,
        output_file=args.output,
        translate=not args.no_translate,
        sample_size=args.sample
    )


if __name__ == "__main__":
    main()

