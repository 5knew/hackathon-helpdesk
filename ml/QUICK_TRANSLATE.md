# Быстрый старт: Перевод датасета

## Шаг 1: Установка зависимостей

```bash
pip install deep-translator tqdm
```

## Шаг 2: Тестирование на выборке

Сначала протестируйте на небольшой выборке (10-50 строк):

```bash
python translate_and_transform_dataset.py --sample 50
```

Это создаст файл `datasets/dataset_translated_ru_kz.csv` с переведенными данными.

## Шаг 3: Полный перевод (опционально)

Если тест прошел успешно, можно перевести весь датасет:

```bash
python translate_and_transform_dataset.py
```

**Внимание:** Это может занять много времени (несколько часов для большого датасета).

## Шаг 4: Использование переведенного датасета

После перевода используйте стандартный pipeline:

```bash
# 1. Подготовка (если нужно)
python prepare_dataset.py

# 2. Обучение моделей
python train_classifiers.py
```

## Что делает скрипт:

1. ✅ Загружает исходный датасет
2. ✅ Для каждой строки создает 2 копии (RU и KZ)
3. ✅ Переводит все тексты (subject, body, answer) на соответствующий язык
4. ✅ Сохраняет кэш переводов для ускорения
5. ✅ Создает новый датасет с колонкой `language` = 'ru' или 'kz'

## Результат:

- Исходный датасет: 28,587 строк
- После перевода: ~57,174 строк (28,587 × 2)
- 50% на русском, 50% на казахском

## Параметры:

- `--sample N` - обработать только N строк (для тестирования)
- `--input FILE` - указать входной файл
- `--output FILE` - указать выходной файл
- `--no-translate` - не переводить, только дублировать

## Примеры:

```bash
# Тест на 100 строках
python translate_and_transform_dataset.py --sample 100

# Перевод конкретного файла
python translate_and_transform_dataset.py \
  --input datasets/dataset_preprocessed.csv \
  --output datasets/dataset_ru_kz.csv

# Только дублирование без перевода
python translate_and_transform_dataset.py --no-translate
```

