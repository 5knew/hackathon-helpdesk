#!/bin/bash
# Скрипт для запуска ML сервиса

echo "=========================================="
echo "Запуск ML сервиса Help Desk"
echo "=========================================="

# Проверка наличия моделей
MODELS_DIR="models"
REQUIRED_MODELS=(
    "classifier_category.pkl"
    "classifier_priority.pkl"
    "classifier_problem_type.pkl"
)

echo "Проверка наличия моделей..."
for model in "${REQUIRED_MODELS[@]}"; do
    if [ ! -f "$MODELS_DIR/$model" ]; then
        echo "❌ Ошибка: Модель $model не найдена!"
        echo "   Сначала обучите модели: python train_classifiers.py"
        exit 1
    fi
done

echo "✅ Все модели найдены"

# Проверка наличия responses.json
if [ ! -f "responses.json" ]; then
    echo "⚠️  Предупреждение: файл responses.json не найден"
    echo "   Автоответ будет недоступен"
fi

echo ""
echo "Запуск сервиса на http://localhost:8000"
echo "Документация API: http://localhost:8000/docs"
echo "=========================================="
echo ""

# Запуск app.py (современная версия)
python app.py

