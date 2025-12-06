"""
Utility functions for ticket history tracking
"""
from sqlalchemy.orm import Session
from models.ticket_history import TicketHistory, HistoryAction
from models.ticket import Ticket, TicketStatus, TicketPriority
from uuid import UUID
from typing import Optional


def log_ticket_creation(ticket: Ticket, db: Session, user_id: Optional[UUID] = None):
    """Записывает создание тикета в историю"""
    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user_id or ticket.user_id,
        action=HistoryAction.CREATED,
        description=f"Тикет создан: {ticket.subject or ticket.body[:50]}"
    )
    db.add(history)


def log_status_change(
    ticket: Ticket,
    old_status: TicketStatus,
    new_status: TicketStatus,
    db: Session,
    user_id: Optional[UUID] = None
):
    """Записывает изменение статуса в историю"""
    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user_id,
        action=HistoryAction.STATUS_CHANGED,
        old_value=old_status.value,
        new_value=new_status.value,
        description=f"Статус изменен: {old_status.value} → {new_status.value}"
    )
    db.add(history)


def log_priority_change(
    ticket: Ticket,
    old_priority: Optional[TicketPriority],
    new_priority: TicketPriority,
    db: Session,
    user_id: Optional[UUID] = None
):
    """Записывает изменение приоритета в историю"""
    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user_id,
        action=HistoryAction.PRIORITY_CHANGED,
        old_value=old_priority.value if old_priority else None,
        new_value=new_priority.value,
        description=f"Приоритет изменен: {old_priority.value if old_priority else 'не установлен'} → {new_priority.value}"
    )
    db.add(history)


def log_assignment(
    ticket: Ticket,
    operator_id: Optional[UUID],
    db: Session,
    user_id: Optional[UUID] = None
):
    """Записывает назначение оператора в историю"""
    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user_id,
        action=HistoryAction.ASSIGNED,
        new_value=str(operator_id) if operator_id else None,
        description=f"Тикет назначен оператору: {operator_id}" if operator_id else "Назначение оператора снято"
    )
    db.add(history)


def log_comment_added(
    ticket: Ticket,
    db: Session,
    user_id: Optional[UUID] = None
):
    """Записывает добавление комментария в историю"""
    history = TicketHistory(
        ticket_id=ticket.id,
        user_id=user_id,
        action=HistoryAction.COMMENT_ADDED,
        description="Добавлен комментарий"
    )
    db.add(history)

