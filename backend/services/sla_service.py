"""
SLA Service - расчет SLA и автоматическая эскалация
"""
from datetime import datetime, timedelta
from models.ticket import Ticket, TicketPriority
from models.ticket_history import TicketHistory, HistoryAction
from sqlalchemy.orm import Session


class SLAService:
    """Сервис для работы с SLA"""
    
    # SLA в часах по приоритетам
    SLA_HOURS = {
        TicketPriority.CRITICAL: 1,  # 1 час для критических
        TicketPriority.HIGH: 4,  # 4 часа для высоких
        TicketPriority.MEDIUM: 24,  # 24 часа для средних
        TicketPriority.LOW: 72  # 72 часа для низких
    }
    
    @staticmethod
    def calculate_sla_deadline(priority: TicketPriority, created_at: datetime) -> datetime:
        """
        Рассчитывает дедлайн SLA на основе приоритета
        """
        hours = SLAService.SLA_HOURS.get(priority, 24)  # По умолчанию 24 часа
        return created_at + timedelta(hours=hours)
    
    @staticmethod
    def check_sla_status(ticket: Ticket) -> str:
        """
        Проверяет статус SLA тикета
        Возвращает: 'ok', 'warning', 'overdue', 'met'
        """
        if ticket.status.value == "closed" or ticket.status.value == "auto_resolved":
            return "met"
        
        if not ticket.sla_deadline:
            return "ok"
        
        now = datetime.utcnow()
        time_left = ticket.sla_deadline - now
        
        if time_left.total_seconds() < 0:
            return "overdue"  # Просрочено
        elif time_left.total_seconds() < 3600:  # Меньше часа
            return "warning"  # Предупреждение
        else:
            return "ok"
    
    @staticmethod
    def should_escalate(ticket: Ticket) -> bool:
        """
        Проверяет, нужно ли эскалировать тикет
        """
        if ticket.is_escalated:
            return False  # Уже эскалирован
        
        if not ticket.sla_deadline:
            return False
        
        now = datetime.utcnow()
        time_left = ticket.sla_deadline - now
        
        # Эскалируем если осталось меньше 12 часов до дедлайна
        return time_left.total_seconds() < 12 * 3600 and time_left.total_seconds() > 0
    
    @staticmethod
    def escalate_ticket(ticket: Ticket, db: Session, user_id=None) -> bool:
        """
        Эскалирует тикет (повышает приоритет и создает запись в истории)
        """
        if ticket.is_escalated:
            return False  # Уже эскалирован
        
        # Повышаем приоритет
        if ticket.priority == TicketPriority.LOW:
            ticket.priority = TicketPriority.MEDIUM
        elif ticket.priority == TicketPriority.MEDIUM:
            ticket.priority = TicketPriority.HIGH
        elif ticket.priority == TicketPriority.HIGH:
            ticket.priority = TicketPriority.CRITICAL
        
        # Пересчитываем SLA с новым приоритетом
        ticket.sla_deadline = SLAService.calculate_sla_deadline(
            ticket.priority,
            ticket.created_at
        )
        
        ticket.is_escalated = True
        ticket.updated_at = datetime.utcnow()
        
        # Создаем запись в истории
        history = TicketHistory(
            ticket_id=ticket.id,
            user_id=user_id,
            action=HistoryAction.ESCALATED,
            description=f"Тикет автоматически эскалирован. Новый приоритет: {ticket.priority.value}",
            old_value=ticket.priority.value if ticket.priority else None,
            new_value=ticket.priority.value
        )
        db.add(history)
        
        db.commit()
        db.refresh(ticket)
        
        return True

