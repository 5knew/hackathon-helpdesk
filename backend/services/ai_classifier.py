"""
AI Classifier Service - классификация тикетов с помощью ML
"""
import requests
import os
from typing import Dict, Optional
from models.ticket import TicketPriority, IssueType


class AIClassifier:
    """Сервис для классификации тикетов с помощью ML модели"""
    
    def __init__(self):
        self.ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8000")
    
    def classify(
        self, 
        subject: str, 
        body: str
    ) -> Dict:
        """
        Классифицирует тикет и возвращает категорию, приоритет, тип проблемы и уверенность
        
        Returns:
            {
                "category": str,
                "priority": TicketPriority,
                "issue_type": IssueType,
                "confidence": {
                    "category": float,
                    "priority": float,
                    "problem_type": float
                }
            }
        """
        try:
            payload = {
                "subject": subject or "Заявка",
                "body": body
            }
            response = requests.post(
                f"{self.ml_service_url}/predict",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Преобразуем ответ ML сервиса в нужный формат
            return {
                "category": result.get("category", "Общие вопросы"),
                "priority": self._map_priority(result.get("priority", "Средний")),
                "issue_type": self._map_issue_type(result.get("problem_type", "Сложный")),
                "confidence": result.get("confidence", {
                    "category": 0.5,
                    "priority": 0.5,
                    "problem_type": 0.5
                })
            }
        except requests.exceptions.RequestException as e:
            print(f"Error calling ML service: {e}")
            # Fallback значения
            return {
                "category": "Общие вопросы",
                "priority": TicketPriority.MEDIUM,
                "issue_type": IssueType.COMPLEX,
                "confidence": {
                    "category": 0.3,
                    "priority": 0.3,
                    "problem_type": 0.3
                }
            }
    
    def _map_priority(self, priority_str: str) -> TicketPriority:
        """Преобразует строку приоритета в enum"""
        mapping = {
            "Низкий": TicketPriority.LOW,
            "Средний": TicketPriority.MEDIUM,
            "Высокий": TicketPriority.HIGH,
            "Критический": TicketPriority.CRITICAL,
        }
        return mapping.get(priority_str, TicketPriority.MEDIUM)
    
    def _map_issue_type(self, issue_type_str: str) -> IssueType:
        """Преобразует строку типа проблемы в enum"""
        mapping = {
            "Типовой": IssueType.AUTO_RESOLVABLE,
            "Простой": IssueType.SIMPLE,
            "Сложный": IssueType.COMPLEX,
        }
        return mapping.get(issue_type_str, IssueType.COMPLEX)

