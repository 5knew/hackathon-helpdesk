"""
AI Router Service - маршрутизация тикетов по департаментам
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.department import Department
from models.category import Category


class AIRouter:
    """Сервис для маршрутизации тикетов по департаментам"""
    
    def route_ticket(
        self,
        db: Session,
        category_name: str,
        priority: str,
        confidence: float
    ) -> Optional[UUID]:
        """
        Определяет департамент для тикета на основе категории
        
        Args:
            db: Сессия БД
            category_name: Название категории
            priority: Приоритет
            confidence: Уверенность модели
            
        Returns:
            UUID департамента или None
        """
        # Если уверенность низкая, не маршрутизируем
        if confidence < 0.7:
            return None
        
        # Логика маршрутизации по категории
        category_lower = category_name.lower()
        
        # Ищем существующий департамент по категории
        if "биллинг" in category_lower or "платеж" in category_lower:
            dept = db.query(Department).filter(Department.name.ilike("%Billing%")).first()
            if dept:
                return dept.id
        
        if "техническая" in category_lower or "it" in category_lower:
            dept = db.query(Department).filter(Department.name.ilike("%Tech%")).first()
            if dept:
                return dept.id
        
        if "hr" in category_lower or "кадр" in category_lower:
            dept = db.query(Department).filter(Department.name.ilike("%HR%")).first()
            if dept:
                return dept.id
        
        if "клиентский" in category_lower or "сервис" in category_lower:
            dept = db.query(Department).filter(Department.name.ilike("%Customer%")).first()
            if dept:
                return dept.id
        
        # По умолчанию - общая поддержка
        dept = db.query(Department).filter(Department.name.ilike("%General%")).first()
        if dept:
            return dept.id
        
        return None

