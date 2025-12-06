import { Ticket, Comment, TicketHistory, TicketFilter, Template, Integration } from '../types';
import { storage } from './storage';
import { apiRequest } from './apiConfig';
import { api } from './apiGenerated';

/**
 * ВНИМАНИЕ: Этот файл содержит старые API функции.
 * Для эндпоинтов, которые есть в новом API (/tickets, /tickets/{id}), используйте api.tickets.* из apiGenerated.ts
 * Эти функции оставлены для обратной совместимости и для эндпоинтов, которых нет в новом API (comments, history, templates, integrations)
 */

// Получить все тикеты пользователя
// УСТАРЕЛО: Используйте api.tickets.list() из apiGenerated.ts
// Оставлено для обратной совместимости
export async function getUserTickets(filter?: TicketFilter): Promise<Ticket[]> {
  try {
    // Используем новый сгенерированный API
    const statusMap: Record<string, 'new' | 'auto_resolved' | 'in_work' | 'waiting' | 'closed'> = {
      'Open': 'new',
      'In Progress': 'in_work',
      'Pending': 'waiting',
      'Closed': 'closed'
    };
    
    const status = filter?.status && filter.status.length > 0 
      ? statusMap[filter.status[0]] || undefined 
      : undefined;
    
    const tickets = await api.tickets.list({ status });
    
    // Преобразуем новые типы в старые для обратной совместимости
    return tickets.map(t => ({
      id: parseInt(t.id) || 0,
      user_id: t.user_id,
      problem_description: t.body,
      status: t.status,
      category: t.category_id || '',
      priority: t.priority || '',
      queue: t.assigned_department_id || '',
      problem_type: t.issue_type || '',
      needs_clarification: t.ai_confidence !== null && t.ai_confidence < 0.7,
      subject: t.subject || '',
      created_at: t.created_at,
      updated_at: t.updated_at,
      closed_at: t.closed_at || undefined
    }));
  } catch (error) {
    console.error('Error fetching tickets:', error);
    // Возвращаем пустой массив вместо моков
    return [];
  }
}

// Получить тикет по ID
// УСТАРЕЛО: Используйте api.tickets.getById() из apiGenerated.ts
// Оставлено для обратной совместимости
export async function getTicketById(ticketId: number): Promise<Ticket | null> {
  try {
    // Используем новый сгенерированный API
    const ticket = await api.tickets.getById(ticketId.toString());
    
    // Преобразуем новый тип в старый для обратной совместимости
    return {
      id: parseInt(ticket.id) || ticketId,
      user_id: ticket.user_id,
      problem_description: ticket.body,
      status: ticket.status,
      category: ticket.category_id || '',
      priority: ticket.priority || '',
      queue: ticket.assigned_department_id || '',
      problem_type: ticket.issue_type || '',
      needs_clarification: ticket.ai_confidence !== null && ticket.ai_confidence < 0.7,
      subject: ticket.subject || '',
      created_at: ticket.created_at,
      updated_at: ticket.updated_at,
      closed_at: ticket.closed_at || undefined
    };
  } catch (error) {
    console.error('Error fetching ticket:', error);
    return null;
  }
}

// Получить комментарии тикета
// ВНИМАНИЕ: Эндпоинт /tickets/{id}/comments пока не реализован в новом API
// Используется старый API
export async function getTicketComments(ticketId: number | string): Promise<Comment[]> {
  try {
    const ticketIdStr = typeof ticketId === 'string' ? ticketId : ticketId.toString();
    const comments = await apiRequest<Comment[]>(`/tickets/${ticketIdStr}/comments`);
    // Преобразуем для обратной совместимости
    return comments.map(c => {
      // Определяем тип автора на основе роли
      let authorType: 'user' | 'operator' | 'system' | 'admin' = 'user';
      if (c.is_auto_reply) {
        authorType = 'system';
      } else if (c.user_role === 'admin') {
        authorType = 'admin';
      } else if (c.user_role === 'employee') {
        authorType = 'operator';
      }
      
      // Формируем имя автора с учетом роли
      let authorName = c.user_name || c.user_email || c.user_id || 'Неизвестный пользователь';
      if (c.user_role === 'admin') {
        authorName = `👨‍💼 Администратор${c.user_name ? ` (${c.user_name})` : ''}`;
      } else if (c.user_role === 'employee') {
        authorName = `👨‍💼 Оператор${c.user_name ? ` (${c.user_name})` : ''}`;
      }
      
      return {
        ...c,
        author: authorName,
        text: c.comment_text,
        author_type: authorType
      };
    });
  } catch (error) {
    console.error('Error fetching comments:', error);
    // Возвращаем пустой массив вместо моков
    return [];
  }
}

// Добавить комментарий
export async function addComment(ticketId: number | string, text: string): Promise<Comment> {
  const user = storage.getUser();
  const ticketIdStr = typeof ticketId === 'string' ? ticketId : ticketId.toString();
  try {
    const comment = await apiRequest<Comment>(`/tickets/${ticketIdStr}/comments`, {
      method: 'POST',
      body: JSON.stringify({
        comment_text: text,
        is_auto_reply: false
      })
    });
    // Преобразуем для обратной совместимости
    return {
      ...comment,
      author: comment.user_id,
      text: comment.comment_text,
      author_type: 'user' as const
    };
  } catch (error) {
    console.error('Error adding comment:', error);
    // Пробрасываем ошибку дальше вместо возврата мока
    throw error;
  }
}

// Получить историю изменений тикета
// ВНИМАНИЕ: Эндпоинт /tickets/{id}/history пока не реализован в новом API
// Возвращаем моковые данные
export async function getTicketHistory(ticketId: number | string): Promise<TicketHistory[]> {
  const ticketIdStr = typeof ticketId === 'string' ? ticketId : ticketId.toString();
  return apiRequest<TicketHistory[]>(`/tickets/${ticketIdStr}/history`);
  try {
    // Эндпоинт /tickets/{id}/history пока не реализован в backend
    // Возвращаем моковые данные
    return [];
  } catch (error) {
    console.error('Error fetching history:', error);
    return [];
  }
}

// Mock function removed - using real API only

// Обновить статус тикета
// УСТАРЕЛО: Используйте api.tickets.update() из apiGenerated.ts
// Оставлено для обратной совместимости
export async function updateTicketStatus(ticketId: number, status: string): Promise<Ticket> {
  try {
    // Используем новый сгенерированный API
    const ticket = await api.tickets.update(ticketId.toString(), {
      status: status as any
    });
    
    // Преобразуем новый тип в старый для обратной совместимости
    return {
      id: parseInt(ticket.id) || ticketId,
      user_id: ticket.user_id,
      problem_description: ticket.body,
      status: ticket.status,
      category: ticket.category_id || '',
      priority: ticket.priority || '',
      queue: ticket.assigned_department_id || '',
      problem_type: ticket.issue_type || '',
      needs_clarification: ticket.ai_confidence !== null && ticket.ai_confidence < 0.7,
      subject: ticket.subject || '',
      created_at: ticket.created_at,
      updated_at: ticket.updated_at,
      closed_at: ticket.closed_at || undefined
    };
  } catch (error) {
    console.error('Error updating ticket:', error);
    throw error;
  }
}

// Отправить CSAT оценку
export async function submitCSAT(ticketId: number, score: number, comment?: string): Promise<void> {
  try {
    await apiRequest(`/tickets/${ticketId}/feedback`, {
      method: 'POST',
      body: JSON.stringify({ rating: score, comment })
    });
  } catch (error) {
    console.error('Error submitting CSAT:', error);
  }
}

// Получить шаблоны ответов
// ВНИМАНИЕ: Эндпоинт /templates пока не реализован в новом API
// Используется старый API или моки
export async function getTemplates(category?: string): Promise<Template[]> {
  try {
    const url = category ? `/templates?category=${category}` : '/templates';
    const templates = await apiRequest<Template[]>(url);
    // Преобразуем для обратной совместимости
    return templates.map(t => ({
      ...t,
      text: t.content,
      language: 'ru' as const
    }));
  } catch (error) {
    console.error('Error fetching templates:', error);
    return [];
  }
}

// Получить интеграции
// ВНИМАНИЕ: Эндпоинт /integrations пока не реализован в новом API
// Возвращаем пустой массив
export async function getIntegrations(): Promise<Integration[]> {
  try {
    // Эндпоинт пока не реализован в backend
    return [];
  } catch (error) {
    console.error('Error fetching integrations:', error);
    return [];
  }
}

// All mock functions removed - using real API only

