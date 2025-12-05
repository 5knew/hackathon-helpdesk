"""
Модуль автоматического ответа на типовые вопросы
Использует FAISS для семантического поиска по шаблонам ответов
"""

import json
import os
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import Optional, Dict, Tuple
import joblib


class AutoReplyService:
    """Сервис для автоматического ответа на типовые вопросы"""
    
    def __init__(self, responses_path: str = "responses.json",
                 model_path: str = None,
                 similarity_threshold: float = 0.65,
                 index_path: str = "models/faiss_index.bin",
                 metadata_path: str = "models/faiss_index_meta.json"):
        """
        Инициализация сервиса автоответа
        
        Args:
            responses_path: путь к файлу с шаблонами ответов
            model_path: путь к модели sentence-transformers (если None, загружается из models/)
            similarity_threshold: порог схожести для автоответа (0-1)
            index_path: путь для сохранения/загрузки FAISS индекса
            metadata_path: путь для сохранения/загрузки метаданных индекса
        """
        self.similarity_threshold = similarity_threshold
        self.responses_path = responses_path
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        # Загрузка модели эмбеддингов
        print("Загрузка модели для эмбеддингов...")
        if model_path is None:
            model_path = "models/sentence_transformer_model"
        
        if os.path.exists(model_path):
            self.model = SentenceTransformer(model_path)
        else:
            # Используем предобученную модель
            print(f"Модель не найдена в {model_path}, используем предобученную...")
            self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        # Загрузка шаблонов ответов
        self.responses = self._load_responses()
        
        # Создание/загрузка FAISS индекса
        self.index = None
        self.response_texts = []
        self.response_metadata = []
        if not self._load_cached_index():
            self._build_index()
    
    def _load_responses(self) -> list:
        """Загружает шаблоны ответов из JSON файла"""
        if not os.path.exists(self.responses_path):
            raise FileNotFoundError(f"Файл {self.responses_path} не найден!")
        
        with open(self.responses_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('responses', [])
    
    def _build_index(self):
        """Создает FAISS индекс для всех шаблонов ответов"""
        print("Построение FAISS индекса для автоответов...")
        
        # Собираем все тексты ответов на русском и казахском
        texts = []
        metadata = []
        
        for resp in self.responses:
            # Добавляем русский вариант
            if 'ru' in resp:
                texts.append(resp['ru'])
                metadata.append({
                    'id': resp['id'],
                    'category': resp.get('category', ''),
                    'language': 'ru',
                    'keywords': resp.get('keywords', [])
                })
            
            # Добавляем казахский вариант
            if 'kz' in resp:
                texts.append(resp['kz'])
                metadata.append({
                    'id': resp['id'],
                    'category': resp.get('category', ''),
                    'language': 'kz',
                    'keywords': resp.get('keywords', [])
                })
        
        if not texts:
            raise ValueError("Не найдено ни одного шаблона ответа!")
        
        self.response_texts = texts

        # Генерация эмбеддингов для всех шаблонов
        print(f"Генерация эмбеддингов для {len(texts)} шаблонов...")
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=32)
        
        # Создание FAISS индекса
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product для косинусного сходства
        
        # Нормализация для косинусного сходства
        faiss.normalize_L2(embeddings)
        
        # Добавление эмбеддингов в индекс
        self.index.add(embeddings.astype('float32'))
        self.response_metadata = metadata

        print(f"✅ FAISS индекс создан: {self.index.ntotal} векторов, размерность {dimension}")

        # Сохраняем индекс и метаданные для ускорения следующих запусков
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "responses_hash": self._responses_hash(),
                "response_texts": self.response_texts,
                "response_metadata": self.response_metadata
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 Индекс и метаданные сохранены в {self.index_path} и {self.metadata_path}")
    
    def _detect_language(self, text: str) -> str:
        """
        Простое определение языка текста
        (можно улучшить, используя библиотеку langdetect)
        """
        # Простая эвристика: считаем кириллицу казахским/русским
        kz_chars = ['ә', 'ғ', 'қ', 'ң', 'ө', 'ұ', 'ү', 'һ', 'і']
        has_kz_chars = any(char in text.lower() for char in kz_chars)
        
        # Если есть специфичные казахские символы, вероятно казахский
        if has_kz_chars:
            return 'kz'
        
        # Иначе считаем русским (можно добавить более точное определение)
        return 'ru'
    
    def find_best_response(self, query: str, category: str = None, 
                          language: str = None, top_k: int = 3) -> Optional[Dict]:
        """
        Находит наиболее подходящий ответ для запроса
        
        Args:
            query: текст запроса пользователя
            category: категория тикета (для фильтрации)
            language: язык ответа ('ru' или 'kz'), если None - определяется автоматически
            top_k: количество кандидатов для возврата
        
        Returns:
            Словарь с ответом или None, если не найден подходящий
        """
        if self.index is None or len(self.response_texts) == 0:
            return None
        
        # Определение языка, если не указан
        if language is None:
            language = self._detect_language(query)
        
        # Генерация эмбеддинга для запроса
        query_embedding = self.model.encode([query])[0]
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Поиск в FAISS индексе
        k = min(top_k * 2, self.index.ntotal)  # Берем больше кандидатов для фильтрации
        similarities, indices = self.index.search(query_embedding, k)
        
        # Фильтрация по языку и категории
        best_match = None
        best_similarity = 0.0
        
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            metadata = self.response_metadata[idx]
            
            # Проверка языка
            if metadata['language'] != language:
                continue
            
            # Проверка категории (если указана)
            if category and metadata['category'] != category:
                continue
            
            # Проверка порога схожести
            if similarity >= self.similarity_threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'response_id': metadata['id'],
                    'text': self.response_texts[idx],
                    'similarity': float(similarity),
                    'category': metadata['category'],
                    'language': metadata['language'],
                    'keywords': metadata.get('keywords', [])
                }
        
        return best_match
    
    def can_auto_reply(self, query: str, problem_type: str, 
                      category: str = None) -> Tuple[bool, Optional[Dict]]:
        """
        Определяет, можно ли дать автоматический ответ
        
        Args:
            query: текст запроса
            problem_type: тип проблемы ('Типовой' или 'Сложный')
            category: категория тикета
        
        Returns:
            Кортеж (можно_ли_ответить, ответ_или_None)
        """
        # Сложные проблемы не обрабатываем автоматически
        if problem_type == 'Сложный':
            return False, None
        
        # Ищем подходящий ответ
        best_response = self.find_best_response(query, category=category)
        
        if best_response and best_response['similarity'] >= self.similarity_threshold:
            return True, best_response
        
        return False, None
    
    def get_auto_reply(self, query: str, problem_type: str, 
                      category: str = None, language: str = None) -> Dict:
        """
        Получает автоматический ответ для запроса
        
        Args:
            query: текст запроса
            problem_type: тип проблемы
            category: категория тикета
            language: язык ответа
        
        Returns:
            Словарь с результатом автоответа
        """
        can_reply, response = self.can_auto_reply(query, problem_type, category)
        
        if can_reply and response:
            return {
                'can_auto_reply': True,
                'response_text': response['text'],
                'response_id': response['response_id'],
                'similarity': response['similarity'],
                'category': response['category'],
                'language': response['language']
            }
        else:
            # Если response есть, но схожесть низкая, возвращаем её
            similarity = response['similarity'] if response and 'similarity' in response else 0.0
            return {
                'can_auto_reply': False,
                'reason': 'Сложный вопрос' if problem_type == 'Сложный' else 'Не найден подходящий шаблон',
                'similarity': similarity
            }


# Функция для сохранения/загрузки индекса (опционально, для ускорения)
def save_index(service: AutoReplyService, index_path: str = "models/faiss_index.bin"):
    """Сохраняет FAISS индекс на диск"""
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(service.index, index_path)
    print(f"✅ FAISS индекс сохранен: {index_path}")


def load_index(index_path: str = "models/faiss_index.bin") -> Optional[faiss.Index]:
    """Загружает FAISS индекс с диска"""
    if os.path.exists(index_path):
        return faiss.read_index(index_path)
    return None


if __name__ == "__main__":
    # Тестирование модуля
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ МОДУЛЯ АВТООТВЕТА")
    print("=" * 60)
    
    # Инициализация сервиса
    service = AutoReplyService()
    
    # Тестовые запросы
    test_queries = [
        ("Как сбросить пароль?", "Типовой", "Общие вопросы"),
        ("Когда нужно оплачивать счет?", "Типовой", "Биллинг и платежи"),
        ("Какие способы оплаты вы принимаете?", "Типовой", "Биллинг и платежи"),
        ("Не могу войти в систему", "Типовой", "Общие вопросы"),
        ("Сервер не отвечает, критическая ошибка", "Сложный", "IT поддержка"),
    ]
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    for query, problem_type, category in test_queries:
        print(f"\n📝 Запрос: {query}")
        print(f"   Тип: {problem_type}, Категория: {category}")
        
        result = service.get_auto_reply(query, problem_type, category)
        
        if result['can_auto_reply']:
            print(f"   ✅ Автоответ возможен (similarity: {result['similarity']:.3f})")
            print(f"   📄 Ответ: {result['response_text'][:100]}...")
        else:
            print(f"   ❌ Автоответ невозможен: {result['reason']}")
            if result.get('similarity', 0) > 0:
                print(f"   (Лучшая схожесть: {result['similarity']:.3f})")

    def _responses_hash(self) -> str:
        """Возвращает контрольную сумму файла с шаблонами ответов"""
        hasher = hashlib.md5()
        with open(self.responses_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _load_cached_index(self) -> bool:
        """
        Пытается загрузить сохраненный FAISS индекс и метаданные, если они
        соответствуют текущему файлу ответов.
        """
        if not (os.path.exists(self.index_path) and os.path.exists(self.metadata_path)):
            return False

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            if metadata.get("responses_hash") != self._responses_hash():
                return False

            self.response_texts = metadata.get("response_texts", [])
            self.response_metadata = metadata.get("response_metadata", [])
            self.index = faiss.read_index(self.index_path)
            print(f"✅ Загружен кешированный FAISS индекс из {self.index_path}")
            return True
        except Exception as exc:  # pragma: no cover - защитный блок
            print(f"⚠️  Не удалось загрузить кешированный индекс: {exc}")
            return False
