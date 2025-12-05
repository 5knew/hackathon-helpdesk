import { Ticket } from '../types';
import { storage } from './storage';

// Имитация email-уведомлений
export function simulateEmailNotification(ticket: Ticket, type: 'created' | 'updated' | 'closed' | 'comment') {
  const user = storage.getUser();
  if (!user) return;

  const notifications = JSON.parse(localStorage.getItem('email_notifications') || '[]');
  
  const notification = {
    id: Date.now(),
    ticket_id: ticket.id,
    ticket_subject: ticket.subject,
    type,
    email: user.email,
    timestamp: new Date().toISOString(),
    read: false,
    message: getNotificationMessage(ticket, type)
  };

  notifications.unshift(notification);
  localStorage.setItem('email_notifications', JSON.stringify(notifications.slice(0, 50)));
  
  // Показываем toast-уведомление
  return notification;
}

function getNotificationMessage(ticket: Ticket, type: string): string {
  switch (type) {
    case 'created':
      return `Ваша заявка #${ticket.id} "${ticket.subject}" создана и принята в обработку.`;
    case 'updated':
      return `Статус заявки #${ticket.id} "${ticket.subject}" изменен на "${ticket.status}".`;
    case 'closed':
      return `Заявка #${ticket.id} "${ticket.subject}" закрыта.`;
    case 'comment':
      return `Новый комментарий в заявке #${ticket.id} "${ticket.subject}".`;
    default:
      return `Обновление по заявке #${ticket.id}`;
  }
}

export function getUnreadNotificationsCount(): number {
  const notifications = JSON.parse(localStorage.getItem('email_notifications') || '[]');
  return notifications.filter((n: any) => !n.read).length;
}

export function markNotificationAsRead(id: number) {
  const notifications = JSON.parse(localStorage.getItem('email_notifications') || '[]');
  const updated = notifications.map((n: any) => 
    n.id === id ? { ...n, read: true } : n
  );
  localStorage.setItem('email_notifications', JSON.stringify(updated));
}

export function getAllNotifications() {
  return JSON.parse(localStorage.getItem('email_notifications') || '[]');
}

