# Подготовка датасета и обучение моделей

## Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

## Шаг 2: Анализ и перемаппинг датасета

### Вариант 1: Использование готового скрипта (без pandas)
```bash
python prepare_dataset.py
```

Этот скрипт:
- Анализирует уникальные значения в датасете
- Применяет перемаппинг категорий и приоритетов
- Добавляет поле `problem_type` (Типовой/Сложный)
- Сохраняет обработанный датасет в `datasets/dataset_preprocessed.csv`
- Сохраняет словари маппинга в `mappings.json`

### Вариант 2: Использование pandas (как в примере)
```bash
python dataset_mapping_example.py
```

## Шаг 3: Обучение моделей классификации

```bash
python train_classifiers.py
```

Этот скрипт:
- Загружает обработанный датасет
- Генерирует эмбеддинги с помощью `sentence-transformers`
- Обучает три классификатора:
  - **Категория** (category)
  - **Приоритет** (priority)
  - **Тип проблемы** (problem_type)
- Сохраняет модели в папку `models/`

**Время выполнения:** ~10-30 минут (зависит от размера датасета и мощности GPU/CPU)

## Шаг 4: Объединение с другими датасетами (опционально)

Если у вас есть дополнительные датасеты:

1. Поместите их в папку `datasets/`
2. Отредактируйте `merge_datasets.py`, добавив пути к вашим датасетам
3. Запустите:

```bash
python merge_datasets.py
```

4. После объединения повторите шаг 3 (обучение моделей)

## Структура файлов

```
ml/
├── datasets/
│   ├── aa_dataset-tickets-multi-lang-5-2-50-version.csv  # Исходный датасет
│   ├── dataset_preprocessed.csv                          # Обработанный датасет
│   ├── dataset_mapped.csv                                # Датасет с перемаппингом (pandas)
│   └── dataset_merged.csv                                # Объединенный датасет
├── models/
│   ├── classifier_category.pkl                          # Классификатор категорий
│   ├── classifier_priority.pkl                          # Классификатор приоритетов
│   ├── classifier_problem_type.pkl                      # Классификатор типов проблем
│   └── sentence_transformer_model/                       # Модель эмбеддингов
├── mappings.json                                         # Словари перемаппинга
├── prepare_dataset.py                                    # Скрипт подготовки (без pandas)
├── dataset_mapping_example.py                            # Пример с pandas
├── train_classifiers.py                                 # Обучение моделей
├── merge_datasets.py                                    # Объединение датасетов
└── requirements.txt                                     # Зависимости
```

## Словари перемаппинга

### Категории (mapping_category)
- `Technical Support` → `Техническая поддержка`
- `IT Support` → `IT поддержка`
- `Product Support` → `Поддержка продукта`
- `Billing and Payments` → `Биллинг и платежи`
- `Customer Service` → `Клиентский сервис`
- `Sales and Pre-Sales` → `Продажи`
- `Returns and Exchanges` → `Возвраты и обмены`
- `Service Outages and Maintenance` → `Сбои и обслуживание`
- `Human Resources` → `HR`
- `General Inquiry` → `Общие вопросы`

### Приоритеты (mapping_priority)
- `high` → `Высокий`
- `medium` → `Средний`
- `low` → `Низкий`

### Типовые категории (для problem_type)
- `Биллинг и платежи`
- `Клиентский сервис`
- `Общие вопросы`

Все остальные категории считаются **Сложными**.

## Использование обученных моделей

После обучения модели можно использовать для классификации новых тикетов:

```python
from sentence_transformers import SentenceTransformer
import joblib

# Загрузка моделей
model = SentenceTransformer("models/sentence_transformer_model")
clf_category = joblib.load("models/classifier_category.pkl")
clf_priority = joblib.load("models/classifier_priority.pkl")
clf_problem_type = joblib.load("models/classifier_problem_type.pkl")

# Классификация нового тикета
ticket_text = "Не могу подключиться к принтеру"
embedding = model.encode([ticket_text])

category = clf_category.predict(embedding)[0]
priority = clf_priority.predict(embedding)[0]
problem_type = clf_problem_type.predict(embedding)[0]

print(f"Категория: {category}")
print(f"Приоритет: {priority}")
print(f"Тип проблемы: {problem_type}")
```

