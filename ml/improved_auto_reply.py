"""
Улучшенный модуль автоматического ответа
Реализует улучшенную генерацию ответов с адаптацией шаблонов
"""

import json
import os
import re
from typing import Optional, Dict, List
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class ImprovedAutoReplyService:
    """Улучшенный сервис автоответа с адаптацией шаблонов"""
    
    def __init__(self, responses_path: str = "responses.json",
                 model_path: str = None,
                 similarity_threshold: float = 0.50):
        """
        Инициализация улучшенного сервиса автоответа
        
        Args:
            responses_path: путь к файлу с шаблонами ответов
            model_path: путь к модели sentence-transformers
            similarity_threshold: порог схожести для автоответа
        """
        self.similarity_threshold = similarity_threshold
        self.responses_path = responses_path
        
        # Загрузка модели эмбеддингов
        print("Загрузка модели для эмбеддингов...")
        if model_path is None:
            model_path = "models/sentence_transformer_model"
        
        if os.path.exists(model_path):
            self.embedding_model = SentenceTransformer(model_path)
        else:
            self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        # Загрузка шаблонов ответов
        self.responses = self._load_responses()
        
        # Создание FAISS индекса
        self.index = None
        self.response_texts = []
        self.response_metadata = []
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
        
        texts = []
        metadata = []
        
        for resp in self.responses:
            if 'ru' in resp:
                texts.append(resp['ru'])
                metadata.append({
                    'id': resp['id'],
                    'category': resp.get('category', ''),
                    'language': 'ru',
                    'keywords': resp.get('keywords', []),
                    'full_response': resp
                })
            
            if 'kz' in resp:
                texts.append(resp['kz'])
                metadata.append({
                    'id': resp['id'],
                    'category': resp.get('category', ''),
                    'language': 'kz',
                    'keywords': resp.get('keywords', []),
                    'full_response': resp
                })
        
        if not texts:
            raise ValueError("Не найдено ни одного шаблона ответа!")
        
        self.response_texts = texts
        
        print(f"Генерация эмбеддингов для {len(texts)} шаблонов...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True, batch_size=32)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        self.response_metadata = metadata
        
        print(f"✅ FAISS индекс создан: {self.index.ntotal} векторов")
    
    def _detect_language(self, text: str) -> str:
        """Определение языка текста"""
        kz_chars = ['ә', 'ғ', 'қ', 'ң', 'ө', 'ұ', 'ү', 'һ', 'і']
        has_kz_chars = any(char in text.lower() for char in kz_chars)
        return 'kz' if has_kz_chars else 'ru'
    
    def _find_similar_responses(self, query: str, category: str = None,
                               language: str = None, top_k: int = 3) -> List[Dict]:
        """Находит похожие ответы через FAISS"""
        if self.index is None or len(self.response_texts) == 0:
            return []
        
        if language is None:
            language = self._detect_language(query)
        
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Увеличиваем количество кандидатов для лучшего поиска
        k = min(top_k * 5, self.index.ntotal)
        similarities, indices = self.index.search(query_embedding, k)
        
        candidates = []
        for similarity, idx in zip(similarities[0], indices[0]):
            metadata = self.response_metadata[idx]
            
            if metadata['language'] != language:
                continue
            
            # Проверка по keywords для улучшения поиска
            similarity_boost = 0.0
            if metadata.get('keywords'):
                query_lower = query.lower()
                matching_keywords = sum(1 for kw in metadata['keywords'] if kw.lower() in query_lower)
                if matching_keywords > 0:
                    similarity_boost = min(0.15, matching_keywords * 0.05)
            
            adjusted_similarity = float(similarity) + similarity_boost
            
            if category and metadata['category'] != category:
                # Не исключаем, но понижаем приоритет (меньше для казахского)
                penalty = 0.05 if language == 'kz' else 0.1
                adjusted_similarity -= penalty
            
            candidates.append({
                'response_id': metadata['id'],
                'text': self.response_texts[idx],
                'similarity': adjusted_similarity,
                'category': metadata['category'],
                'language': metadata['language'],
                'keywords': metadata.get('keywords', []),
                'full_response': metadata.get('full_response', {})
            })
        
        return sorted(candidates, key=lambda x: x['similarity'], reverse=True)[:top_k]
    
    def _generate_template_response(self, query: str, 
                                   similar_responses: List[Dict],
                                   language: str) -> str:
        """Генерирует ответ на основе шаблонов с адаптацией"""
        if not similar_responses:
            return self._get_default_response(language)
        
        best_response = similar_responses[0]
        
        # Если схожесть высокая, используем шаблон как есть
        if best_response.get('similarity', 0) >= 0.8:
            return best_response['text']
        
        # Иначе адаптируем шаблон под запрос
        template = best_response.get('text', '')
        if not template:
            return self._get_default_response(language)
        
        # Добавляем персонализацию
        lang_greetings = {
            'ru': 'Спасибо за обращение! ',
            'kz': 'Хабарласқаныңызға рахмет! '
        }
        
        greeting = lang_greetings.get(language, '')
        if greeting and not template.startswith(greeting):
            template = greeting + template
        
        return template
    
    def _validate_response(self, response: str, language: str) -> str:
        """Проверяет ответ на безопасность"""
        # Проверка на запрещенные действия
        forbidden_patterns = {
            'ru': [
                r'изменить.*базу данных',
                r'удалить.*данные',
                r'предоставить.*пароль',
            ],
            'kz': [
                r'деректер базасын.*өзгерту',
                r'деректерді.*жою',
                r'құпия сөзді.*беру',
            ]
        }
        
        patterns = forbidden_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return self._get_default_response(language)
        
        # Ограничение длины
        if len(response) > 1000:
            response = response[:1000] + "..."
        
        return response.strip()
    
    def _get_default_response(self, language: str) -> str:
        """Возвращает стандартный ответ по умолчанию"""
        defaults = {
            'ru': 'Спасибо за обращение. Ваш запрос принят в работу. Наш специалист свяжется с вами в ближайшее время.',
            'kz': 'Хабарласқаныңызға рахмет. Сіздің сұрағыңыз жұмысқа алынды. Біздің маманы жақын арада сізбен байланысады.'
        }
        return defaults.get(language, defaults['ru'])
    
    def summarize_conversation(self, messages: List[Dict], language: str = None) -> str:
        """Резюмирует диалог для передачи специалисту"""
        if not messages:
            return ""
        
        if language is None:
            language = self._detect_language(messages[0].get('text', ''))
        
        summary_parts = []
        
        lang_labels = {
            'ru': {
                'summary': 'Резюме диалога:',
                'user': 'Пользователь',
                'support': 'Поддержка'
            },
            'kz': {
                'summary': 'Диалог қорытындысы:',
                'user': 'Пайдаланушы',
                'support': 'Қолдау'
            }
        }
        
        labels = lang_labels.get(language, lang_labels['ru'])
        summary_parts.append(labels['summary'])
        
        for msg in messages[-5:]:  # Последние 5 сообщений
            role = labels['user'] if msg.get('role') == 'user' else labels['support']
            text = msg.get('text', '')[:100]
            summary_parts.append(f"{role}: {text}...")
        
        return "\n".join(summary_parts)
    
    def generate_draft_reply(self, query: str, conversation_history: List[Dict] = None,
                           category: str = None, problem_type: str = None,
                           language: str = None) -> Dict:
        """Генерирует draft reply (черновик ответа)"""
        if language is None:
            language = self._detect_language(query)
        
        # Находим похожие ответы
        similar_responses = self._find_similar_responses(
            query, category=category, language=language, top_k=3
        )
        
        # Определяем confidence с учетом языка (для казахского понижаем порог)
        best_similarity = similar_responses[0].get('similarity', 0.0) if similar_responses else 0.0
        
        # Для казахского языка используем более низкий порог из-за особенностей семантики
        threshold = self.similarity_threshold if language == 'ru' else max(0.45, self.similarity_threshold - 0.15)
        
        # Всегда генерируем ответ, если есть похожие ответы (даже с низкой схожестью)
        if not similar_responses:
            response_text = self._get_default_response(language)
        else:
            # Генерируем ответ на основе лучшего совпадения
            response_text = self._generate_template_response(
                query, similar_responses, language
            )
            
            # Валидация
            response_text = self._validate_response(response_text, language)
        
        # Определяем, можно ли автоответить
        can_auto_reply = (
            problem_type == "Типовой" and 
            best_similarity >= threshold and
            len(similar_responses) > 0
        )
        
        return {
            'can_auto_reply': can_auto_reply,
            'response_text': response_text,  # Всегда возвращаем ответ, если есть похожие ответы
            'response_id': similar_responses[0].get('response_id') if similar_responses else None,
            'similarity': best_similarity,
            'category': category or (similar_responses[0].get('category', '') if similar_responses else ''),
            'language': language,
            'reason': None if can_auto_reply else (
                'Сложный вопрос' if problem_type == 'Сложный' else ('Не найден подходящий шаблон' if not similar_responses else f'Низкая схожесть ({best_similarity:.3f} < {threshold:.3f})')
            )
        }
    
    def get_auto_reply(self, query: str, problem_type: str,
                      category: str = None, language: str = None) -> Dict:
        """Получает автоматический ответ для запроса (совместимость со старым API)"""
        return self.generate_draft_reply(
            query=query,
            category=category,
            problem_type=problem_type,
            language=language
        )
