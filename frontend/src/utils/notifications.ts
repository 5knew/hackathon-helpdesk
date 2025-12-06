/**
 * Утилиты для работы с уведомлениями
 */
import { apiRequest } from './apiConfig';

export interface Notification {
  id: string;
  user_id: string;
  ticket_id?: string;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

/**
 * Получить уведомления пользователя
 */
export async function getNotifications(userId: string, unreadOnly: boolean = false): Promise<Notification[]> {
  try {
    const params = new URLSearchParams({ user_id: userId });
    if (unreadOnly) {
      params.append('unread_only', 'true');
    }
    return await apiRequest<Notification[]>(`/notifications?${params.toString()}`);
  } catch (error) {
    console.error('Error fetching notifications:', error);
    return [];
  }
}

/**
 * Получить количество непрочитанных уведомлений
 */
export async function getUnreadCount(userId: string): Promise<number> {
  try {
    const params = new URLSearchParams({ user_id: userId });
    const response = await apiRequest<{ count: number }>(`/notifications/unread/count?${params.toString()}`);
    return response.count;
  } catch (error) {
    console.error('Error fetching unread count:', error);
    return 0;
  }
}

/**
 * Пометить уведомление как прочитанное
 */
export async function markAsRead(notificationId: string, userId: string): Promise<void> {
  try {
    const params = new URLSearchParams({ user_id: userId });
    await apiRequest(`/notifications/${notificationId}/read?${params.toString()}`, {
      method: 'PUT'
    });
  } catch (error) {
    console.error('Error marking notification as read:', error);
    throw error;
  }
}

/**
 * Пометить все уведомления как прочитанные
 */
export async function markAllAsRead(userId: string): Promise<void> {
  try {
    const params = new URLSearchParams({ user_id: userId });
    await apiRequest(`/notifications/read-all?${params.toString()}`, {
      method: 'PUT'
    });
  } catch (error) {
    console.error('Error marking all as read:', error);
    throw error;
  }
}
