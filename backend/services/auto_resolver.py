"""
Auto Resolver Service - автоматическое решение типовых проблем
"""
import requests
import os
from typing import Optional
from models.ticket import IssueType


class AutoResolver:
    """Сервис для автоматического решения типовых проблем"""
    
    def __init__(self):
        self.ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8000")
    
    def try_auto_resolve(
        self,
        text: str,
        category: Optional[str] = None,
        issue_type: Optional[IssueType] = None
    ) -> Optional[str]:
        """
        Пытается автоматически решить проблему
        
        Args:
            text: Текст тикета
            category: Категория
            issue_type: Тип проблемы
            
        Returns:
            Текст автоматического ответа или None, если не удалось решить
        """
        # Автоматическое решение только для типовых проблем
        if issue_type != IssueType.AUTO_RESOLVABLE:
            return None
        
        try:
            # Маппинг IssueType enum в строки, которые ожидает ML сервис
            problem_type_map = {
                IssueType.AUTO_RESOLVABLE: "Типовой",
                IssueType.SIMPLE: "Простой",
                IssueType.COMPLEX: "Сложный"
            }
            
            payload = {"text": text}
            if category:
                payload["category"] = category
            if issue_type:
                payload["problem_type"] = problem_type_map.get(issue_type, "Сложный")
            
            response = requests.post(
                f"{self.ml_service_url}/auto_reply",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Проверяем, может ли система ответить автоматически
            # ML сервис (app.py) возвращает response_text, а не reply
            if result.get("can_auto_reply", False):
                return result.get("response_text", None)
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error calling ML service for auto-reply: {e}")
            return None

