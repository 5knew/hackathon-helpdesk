import { Ticket, Comment, TicketHistory, TicketFilter, Template, Integration, TicketListResponse } from '../types';
import { storage } from './storage';
import { apiRequest } from './apiConfig';

// Получить все тикеты пользователя
export async function getUserTickets(filter?: TicketFilter): Promise<Ticket[]> {
  const user = storage.getUser();
  const userEmail = user?.email || 'guest@user.com';
  
  try {
    const params = new URLSearchParams();
    params.append('user_id', userEmail);
    if (filter?.status && filter.status.length > 0) params.append('status', filter.status[0]);
    if (filter?.category && filter.category.length > 0) params.append('category', filter.category[0]);
    if (filter?.dateFrom) params.append('date_from', filter.dateFrom);
    if (filter?.dateTo) params.append('date_to', filter.dateTo);
    
    const response: TicketListResponse = await apiRequest(`/tickets?${params.toString()}`);
    return response.tickets;
  } catch (error) {
    console.error('Error fetching tickets:', error);
    // Возвращаем моковые данные для демо
    return getMockTickets();
  }
}

// Получить тикет по ID
export async function getTicketById(ticketId: number): Promise<Ticket | null> {
  try {
    return await apiRequest<Ticket>(`/tickets/${ticketId}`);
  } catch (error) {
    console.error('Error fetching ticket:', error);
    return null;
  }
}

// Получить комментарии тикета
export async function getTicketComments(ticketId: number): Promise<Comment[]> {
  try {
    const comments = await apiRequest<Comment[]>(`/tickets/${ticketId}/comments`);
    // Преобразуем для обратной совместимости
    return comments.map(c => ({
      ...c,
      author: c.user_id,
      text: c.comment_text,
      author_type: c.is_auto_reply ? 'system' : 'user' as const
    }));
  } catch (error) {
    console.error('Error fetching comments:', error);
    // Возвращаем моковые данные для демо
    return getMockComments(ticketId);
  }
}

function getMockComments(ticketId: number): Comment[] {
  const now = new Date();
  return [
    {
      id: 1,
      ticket_id: ticketId,
      user_id: 'AI Assistant',
      comment_text: 'Ваша заявка получена и обрабатывается. Мы свяжемся с вами в ближайшее время.',
      is_auto_reply: true,
      created_at: new Date(now.getTime() - 3600000).toISOString(),
      author: 'AI Assistant',
      author_type: 'system',
      text: 'Ваша заявка получена и обрабатывается. Мы свяжемся с вами в ближайшее время.'
    },
    {
      id: 2,
      ticket_id: ticketId,
      user_id: 'Оператор Иван',
      comment_text: 'Добрый день! Я изучил вашу проблему. Для решения необходимо проверить настройки системы. Сделаю это в течение часа.',
      is_auto_reply: false,
      created_at: new Date(now.getTime() - 1800000).toISOString(),
      author: 'Оператор Иван',
      author_type: 'operator',
      text: 'Добрый день! Я изучил вашу проблему. Для решения необходимо проверить настройки системы. Сделаю это в течение часа.'
    },
    {
      id: 3,
      ticket_id: ticketId,
      user_id: storage.getUser()?.email || 'user@example.com',
      comment_text: 'Спасибо за быстрый ответ! Буду ждать.',
      is_auto_reply: false,
      created_at: new Date(now.getTime() - 900000).toISOString(),
      author: storage.getUser()?.email || 'user@example.com',
      author_type: 'user',
      text: 'Спасибо за быстрый ответ! Буду ждать.'
    }
  ];
}

// Добавить комментарий
export async function addComment(ticketId: number, text: string): Promise<Comment> {
  const user = storage.getUser();
  try {
    const comment = await apiRequest<Comment>(`/tickets/${ticketId}/comments`, {
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
    // Возвращаем моковый комментарий для демо
    return {
      id: Date.now(),
      ticket_id: ticketId,
      user_id: user?.email || 'guest',
      comment_text: text,
      is_auto_reply: false,
      created_at: new Date().toISOString(),
      author: user?.email || 'guest',
      author_type: 'user',
      text: text
    };
  }
}

// Получить историю изменений тикета (пока не реализовано в backend, возвращаем мок)
export async function getTicketHistory(ticketId: number): Promise<TicketHistory[]> {
  try {
    // Эндпоинт /tickets/{id}/history пока не реализован в backend
    // Возвращаем моковые данные
    return getMockHistory(ticketId);
  } catch (error) {
    console.error('Error fetching history:', error);
    return getMockHistory(ticketId);
  }
}

function getMockHistory(ticketId: number): TicketHistory[] {
  const now = new Date();
  return [
    {
      id: 1,
      ticket_id: ticketId,
      action: 'Тикет создан',
      changed_by: 'user@example.com',
      old_value: undefined,
      new_value: 'Open',
      created_at: new Date(now.getTime() - 3600000).toISOString()
    },
    {
      id: 2,
      ticket_id: ticketId,
      action: 'Статус изменен',
      changed_by: 'AI System',
      old_value: 'Open',
      new_value: 'In Progress',
      created_at: new Date(now.getTime() - 3300000).toISOString()
    },
    {
      id: 3,
      ticket_id: ticketId,
      action: 'Приоритет изменен',
      changed_by: 'Оператор Иван',
      old_value: 'Средний',
      new_value: 'Высокий',
      created_at: new Date(now.getTime() - 3000000).toISOString()
    }
  ];
}

// Обновить статус тикета
export async function updateTicketStatus(ticketId: number, status: string): Promise<Ticket> {
  try {
    return await apiRequest<Ticket>(`/tickets/${ticketId}`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
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
    return getMockTemplates();
  }
}

// Получить интеграции (пока не реализовано в backend)
export async function getIntegrations(): Promise<Integration[]> {
  try {
    // Эндпоинт пока не реализован в backend
    return [];
  } catch (error) {
    console.error('Error fetching integrations:', error);
    return [];
  }
}

// Моковые данные для демо
function getMockTickets(): Ticket[] {
  return [
    {
      id: 1,
      user_id: 'user@example.com',
      problem_description: 'При попытке входа выдает ошибку неверного пароля',
      status: 'Closed',
      category: 'Техническая поддержка',
      priority: 'Высокий',
      problem_type: 'Типовой',
      queue: 'TechSupport',
      needs_clarification: false,
      subject: 'Не могу войти в почту',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date(Date.now() - 86400000).toISOString(),
      closed_at: new Date(Date.now() - 86400000).toISOString()
    },
    {
      id: 2,
      user_id: 'user@example.com',
      problem_description: 'Хочу перенести отпуск',
      status: 'Pending',
      category: 'HR',
      priority: 'Средний',
      problem_type: 'Сложный',
      queue: 'GeneralSupport',
      needs_clarification: false,
      subject: 'Нужна помощь с HR системой',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date(Date.now() - 1800000).toISOString(),
      sla_deadline: new Date(Date.now() + 86400000).toISOString()
    }
  ];
}

function getMockTemplates(): Template[] {
  return [
    {
      id: 1,
      name: 'Стандартный ответ',
      category: 'Техническая поддержка',
      content: 'Спасибо за обращение. Наша техническая команда уже работает над решением вашей проблемы.',
      created_at: new Date().toISOString(),
      text: 'Спасибо за обращение. Наша техническая команда уже работает над решением вашей проблемы.',
      language: 'ru'
    },
    {
      id: 2,
      name: 'Биллинг',
      category: 'Биллинг и платежи',
      content: 'Ваш запрос по биллингу получен. Мы обработаем его в течение 1-2 рабочих дней.',
      created_at: new Date().toISOString(),
      text: 'Ваш запрос по биллингу получен. Мы обработаем его в течение 1-2 рабочих дней.',
      language: 'ru'
    }
  ];
}

