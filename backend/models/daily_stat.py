"""
Daily Stat model - статистика для панели администратора
"""
from sqlalchemy import Column, Date, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid

from database import Base


class DailyStat(Base):
    __tablename__ = "daily_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, unique=True, index=True)
    total_tickets = Column(Integer, default=0)
    auto_resolved = Column(Integer, default=0)
    ai_accuracy = Column(Float, nullable=True)  # Средняя точность ИИ за день
    misroutes = Column(Integer, default=0)  # Ошибки маршрутизации
    avg_response_time_sec = Column(Integer, nullable=True)  # Среднее время ответа в секундах

