import { Ticket, Comment, TicketHistory, TicketFilter, Template, Integration } from '../types';
import { storage } from './storage';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// Получить все тикеты пользователя
export async function getUserTickets(filter?: TicketFilter): Promise<Ticket[]> {
  const user = storage.getUser();
  const userEmail = user?.email || 'guest@user.com';
  
  try {
    const params = new URLSearchParams();
    if (filter?.status) params.append('status', filter.status.join(','));
    if (filter?.category) params.append('category', filter.category.join(','));
    if (filter?.priority) params.append('priority', filter.priority.join(','));
    if (filter?.dateFrom) params.append('date_from', filter.dateFrom);
    if (filter?.dateTo) params.append('date_to', filter.dateTo);
    if (filter?.search) params.append('search', filter.search);
    
    const response = await fetch(`${API_BASE_URL}/tickets?user_id=${userEmail}&${params.toString()}`);
    if (!response.ok) throw new Error('Failed to fetch tickets');
    return await response.json();
  } catch (error) {
    console.error('Error fetching tickets:', error);
    // Возвращаем моковые данные для демо
    return getMockTickets();
  }
}

// Получить тикет по ID
export async function getTicketById(ticketId: number): Promise<Ticket | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`);
    if (!response.ok) throw new Error('Failed to fetch ticket');
    return await response.json();
  } catch (error) {
    console.error('Error fetching ticket:', error);
    return null;
  }
}

// Получить комментарии тикета
export async function getTicketComments(ticketId: number): Promise<Comment[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`);
    if (!response.ok) throw new Error('Failed to fetch comments');
    return await response.json();
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
      author: 'AI Assistant',
      author_type: 'system',
      text: 'Ваша заявка получена и обрабатывается. Мы свяжемся с вами в ближайшее время.',
      created_at: new Date(now.getTime() - 3600000).toISOString(),
      is_auto_reply: true
    },
    {
      id: 2,
      ticket_id: ticketId,
      author: 'Оператор Иван',
      author_type: 'operator',
      text: 'Добрый день! Я изучил вашу проблему. Для решения необходимо проверить настройки системы. Сделаю это в течение часа.',
      created_at: new Date(now.getTime() - 1800000).toISOString(),
      is_auto_reply: false
    },
    {
      id: 3,
      ticket_id: ticketId,
      author: storage.getUser()?.email || 'user@example.com',
      author_type: 'user',
      text: 'Спасибо за быстрый ответ! Буду ждать.',
      created_at: new Date(now.getTime() - 900000).toISOString(),
      is_auto_reply: false
    }
  ];
}

// Добавить комментарий
export async function addComment(ticketId: number, text: string): Promise<Comment> {
  const user = storage.getUser();
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        author: user?.email || 'guest',
        author_type: 'user'
      })
    });
    if (!response.ok) throw new Error('Failed to add comment');
    return await response.json();
  } catch (error) {
    console.error('Error adding comment:', error);
    // Возвращаем моковый комментарий для демо
    return {
      id: Date.now(),
      ticket_id: ticketId,
      author: user?.email || 'guest',
      author_type: 'user',
      text,
      created_at: new Date().toISOString(),
      is_auto_reply: false
    };
  }
}

// Получить историю изменений тикета
export async function getTicketHistory(ticketId: number): Promise<TicketHistory[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}/history`);
    if (!response.ok) throw new Error('Failed to fetch history');
    return await response.json();
  } catch (error) {
    console.error('Error fetching history:', error);
    // Возвращаем моковые данные для демо
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
    const response = await fetch(`${API_BASE_URL}/tickets/${ticketId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!response.ok) throw new Error('Failed to update ticket');
    return await response.json();
  } catch (error) {
    console.error('Error updating ticket:', error);
    throw error;
  }
}

// Отправить CSAT оценку
export async function submitCSAT(ticketId: number, score: number, comment?: string): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/tickets/${ticketId}/csat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ score, comment })
    });
  } catch (error) {
    console.error('Error submitting CSAT:', error);
  }
}

// Получить шаблоны ответов
export async function getTemplates(category?: string): Promise<Template[]> {
  try {
    const url = category 
      ? `${API_BASE_URL}/templates?category=${category}`
      : `${API_BASE_URL}/templates`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch templates');
    return await response.json();
  } catch (error) {
    console.error('Error fetching templates:', error);
    return getMockTemplates();
  }
}

// Получить интеграции
export async function getIntegrations(): Promise<Integration[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/integrations`);
    if (!response.ok) throw new Error('Failed to fetch integrations');
    return await response.json();
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
      subject: 'Не могу войти в почту',
      problem_description: 'При попытке входа выдает ошибку неверного пароля',
      status: 'Closed',
      category: 'Техническая поддержка',
      priority: 'Высокий',
      problem_type: 'Типовой',
      queue: 'TechSupport',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date(Date.now() - 86400000).toISOString(),
      closed_at: new Date(Date.now() - 86400000).toISOString(),
      auto_closed: true,
      csat_score: 5
    },
    {
      id: 2,
      user_id: 'user@example.com',
      subject: 'Нужна помощь с HR системой',
      problem_description: 'Хочу перенести отпуск',
      status: 'In Progress',
      category: 'HR',
      priority: 'Средний',
      problem_type: 'Сложный',
      queue: 'GeneralSupport',
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
      text: 'Спасибо за обращение. Наша техническая команда уже работает над решением вашей проблемы.',
      language: 'ru'
    },
    {
      id: 2,
      name: 'Биллинг',
      category: 'Биллинг и платежи',
      text: 'Ваш запрос по биллингу получен. Мы обработаем его в течение 1-2 рабочих дней.',
      language: 'ru'
    }
  ];
}

