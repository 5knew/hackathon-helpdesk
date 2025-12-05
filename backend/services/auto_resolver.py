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
            payload = {"text": text}
            if category:
                payload["category"] = category
            if issue_type:
                payload["problem_type"] = issue_type.value
            
            response = requests.post(
                f"{self.ml_service_url}/auto_reply",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Проверяем, может ли система ответить автоматически
            if result.get("can_auto_reply", True):
                return result.get("reply", None)
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error calling ML service for auto-reply: {e}")
            return None

