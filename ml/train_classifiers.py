"""
Файн-тюнинг модели для классификации тикетов
Использует sentence-transformers + классификаторы
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

print("=" * 60)
print("ОБУЧЕНИЕ КЛАССИФИКАТОРОВ")
print("=" * 60)

# Загрузка обработанного датасета
print("\n1. Загрузка датасета...")
df = pd.read_csv("datasets/dataset_preprocessed.csv")

# Проверка наличия необходимых колонок
required_cols = ['category', 'priority', 'problem_type']
for col in required_cols:
    if col not in df.columns:
        print(f"⚠️  Колонка '{col}' не найдена!")
        exit(1)

# Создание текстового поля для классификации (объединяем subject и body)
print("\n2. Подготовка текстовых данных...")
df['text'] = df['subject'].fillna('') + ' ' + df['body'].fillna('')
df = df[df['text'].str.strip() != '']  # Удаляем пустые тексты

print(f"   Всего записей: {len(df)}")

# Загрузка модели для эмбеддингов
print("\n3. Загрузка модели sentence-transformers...")
model_path = "models/sentence_transformer_model"
if os.path.exists(model_path):
    print(f"   ✅ Используем сохраненную модель из {model_path}")
    model = SentenceTransformer(model_path)
else:
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    print(f"   ⚠️  Локальной модели нет, загружаем из HuggingFace: {model_name}")
    print("   (Это может занять время и требует интернет-соединения)")
    model = SentenceTransformer(model_name)

# Генерация эмбеддингов
print("\n4. Генерация эмбеддингов (это может занять время)...")
print("   Это может занять несколько минут для большого датасета...")
X = model.encode(df['text'].tolist(), show_progress_bar=True, batch_size=32)
print(f"   Размерность эмбеддингов: {X.shape}")

# Создание директории для моделей
os.makedirs("models", exist_ok=True)

# Обучение классификатора для категорий
print("\n5. Обучение классификатора категорий...")
y_category = df['category'].values
X_train_cat, X_test_cat, y_train_cat, y_test_cat = train_test_split(
    X, y_category, test_size=0.2, random_state=42, stratify=y_category
)

clf_category = LogisticRegression(max_iter=1000, random_state=42)
clf_category.fit(X_train_cat, y_train_cat)

preds_cat = clf_category.predict(X_test_cat)
acc_cat = accuracy_score(y_test_cat, preds_cat)
print(f"   Точность: {acc_cat:.4f}")
print("\n   Отчет по классификации:")
print(classification_report(y_test_cat, preds_cat))

# Сохранение модели категорий
joblib.dump(clf_category, "models/classifier_category.pkl")
print("   ✅ Модель сохранена: models/classifier_category.pkl")

# Обучение классификатора для приоритетов
print("\n6. Обучение классификатора приоритетов...")
y_priority = df['priority'].values
X_train_pri, X_test_pri, y_train_pri, y_test_pri = train_test_split(
    X, y_priority, test_size=0.2, random_state=42, stratify=y_priority
)

clf_priority = LogisticRegression(max_iter=1000, random_state=42)
clf_priority.fit(X_train_pri, y_train_pri)

preds_pri = clf_priority.predict(X_test_pri)
acc_pri = accuracy_score(y_test_pri, preds_pri)
print(f"   Точность: {acc_pri:.4f}")
print("\n   Отчет по классификации:")
print(classification_report(y_test_pri, preds_pri))

# Сохранение модели приоритетов
joblib.dump(clf_priority, "models/classifier_priority.pkl")
print("   ✅ Модель сохранена: models/classifier_priority.pkl")

# Обучение классификатора для типов проблем
print("\n7. Обучение классификатора типов проблем...")
y_problem_type = df['problem_type'].values
X_train_pt, X_test_pt, y_train_pt, y_test_pt = train_test_split(
    X, y_problem_type, test_size=0.2, random_state=42, stratify=y_problem_type
)

clf_problem_type = LogisticRegression(max_iter=1000, random_state=42)
clf_problem_type.fit(X_train_pt, y_train_pt)

preds_pt = clf_problem_type.predict(X_test_pt)
acc_pt = accuracy_score(y_test_pt, preds_pt)
print(f"   Точность: {acc_pt:.4f}")
print("\n   Отчет по классификации:")
print(classification_report(y_test_pt, preds_pt))

# Сохранение модели типов проблем
joblib.dump(clf_problem_type, "models/classifier_problem_type.pkl")
print("   ✅ Модель сохранена: models/classifier_problem_type.pkl")

# Сохранение модели эмбеддингов
print("\n8. Сохранение модели эмбеддингов...")
model.save("models/sentence_transformer_model")
print("   ✅ Модель сохранена: models/sentence_transformer_model")

print("\n" + "=" * 60)
print("ОБУЧЕНИЕ ЗАВЕРШЕНО!")
print("=" * 60)
print("\nИтоговые метрики:")
print(f"  Категория:     {acc_cat:.4f}")
print(f"  Приоритет:     {acc_pri:.4f}")
print(f"  Тип проблемы:  {acc_pt:.4f}")

