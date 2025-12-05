"""
Stats Service - сервис для сбора статистики
"""
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.ticket import Ticket, TicketStatus
from models.daily_stat import DailyStat
from models.ai_prediction import AIPrediction


class StatsService:
    """Сервис для работы со статистикой"""
    
    def update_daily_stats(self, db: Session, target_date: date = None):
        """
        Обновляет дневную статистику
        
        Args:
            db: Сессия БД
            target_date: Дата для обновления (по умолчанию - сегодня)
        """
        if target_date is None:
            target_date = date.today()
        
        # Подсчитываем статистику за день
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        total_tickets = db.query(Ticket).filter(
            Ticket.created_at >= start_datetime,
            Ticket.created_at <= end_datetime
        ).count()
        
        auto_resolved = db.query(Ticket).filter(
            Ticket.created_at >= start_datetime,
            Ticket.created_at <= end_datetime,
            Ticket.auto_resolved == True
        ).count()
        
        # Средняя точность ИИ за день
        avg_confidence = db.query(func.avg(AIPrediction.confidence)).filter(
            AIPrediction.created_at >= start_datetime,
            AIPrediction.created_at <= end_datetime
        ).scalar() or 0.0
        
        # Ошибки маршрутизации (тикеты, которые были перемаршрутизированы)
        # Пока используем простую метрику - тикеты с низкой уверенностью
        misroutes = db.query(Ticket).filter(
            Ticket.created_at >= start_datetime,
            Ticket.created_at <= end_datetime,
            Ticket.ai_confidence < 0.7
        ).count()
        
        # Среднее время ответа (в секундах)
        # Упрощенная метрика - можно улучшить
        avg_response_time = 0.8  # Имитация
        
        # Обновляем или создаем запись
        daily_stat = db.query(DailyStat).filter(
            DailyStat.date == target_date
        ).first()
        
        if daily_stat:
            daily_stat.total_tickets = total_tickets
            daily_stat.auto_resolved = auto_resolved
            daily_stat.ai_accuracy = float(avg_confidence)
            daily_stat.misroutes = misroutes
            daily_stat.avg_response_time_sec = avg_response_time
        else:
            daily_stat = DailyStat(
                date=target_date,
                total_tickets=total_tickets,
                auto_resolved=auto_resolved,
                ai_accuracy=float(avg_confidence),
                misroutes=misroutes,
                avg_response_time_sec=avg_response_time
            )
            db.add(daily_stat)
        
        db.commit()
    
    def get_stats_for_period(
        self,
        db: Session,
        start_date: date,
        end_date: date
    ) -> dict:
        """
        Получает статистику за период
        
        Returns:
            Словарь со статистикой
        """
        stats = db.query(DailyStat).filter(
            DailyStat.date >= start_date,
            DailyStat.date <= end_date
        ).all()
        
        return {
            "total_tickets": sum(s.total_tickets for s in stats),
            "auto_resolved": sum(s.auto_resolved for s in stats),
            "avg_ai_accuracy": sum(s.ai_accuracy or 0 for s in stats) / len(stats) if stats else 0,
            "total_misroutes": sum(s.misroutes for s in stats),
            "avg_response_time": sum(s.avg_response_time_sec or 0 for s in stats) / len(stats) if stats else 0,
        }

