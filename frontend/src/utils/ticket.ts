import { TicketResult, Ticket, TicketListResponse, Comment, Feedback, Template } from '../types';
import { storage } from './storage';
import { apiRequest } from './apiConfig';
import { api } from './apiGenerated';
import type { TicketCreate, TicketResponse, TicketUpdate } from './apiGenerated';

export async function submitTicketToAPI(text: string): Promise<TicketResult> {
  const user = storage.getUser();
  // В новом API user_id должен быть UUID
  const userId = user?.userId || user?.email || 'guest@user.com';
  
  // Разделяем текст на subject и body (если есть перенос строки)
  const lines = text.split('\n');
  const subject = lines[0].substring(0, 100) || 'Заявка';
  const body = text;

  try {
    // Используем новый сгенерированный API
    const ticketData: TicketCreate = {
      source: 'portal',
      user_id: userId, // Должен быть UUID из localStorage (сохраняется при входе)
      subject: subject,
      body: body,
      language: 'ru'
    };
    
    const data: TicketResponse = await api.tickets.create(ticketData);
    
    // Определяем статус на основе результата
    const isAutoClosed = data.status === 'closed' || data.status === 'auto_resolved' || data.auto_resolved;
    
    return {
      status: isAutoClosed ? 'success' : 'warning',
      message: `Заявка ${data.id} создана и обработана`,
      needs_clarification: data.ai_confidence !== null && data.ai_confidence < 0.7,
      confidence_warning: data.ai_confidence !== null && data.ai_confidence < 0.7 
        ? `Низкая уверенность ИИ: ${(data.ai_confidence * 100).toFixed(1)}%` 
        : undefined,
      queue: data.assigned_department_id || undefined
    };
  } catch (error) {
    console.error('Error submitting ticket:', error);
    throw new Error('Ошибка при отправке заявки. Убедитесь, что backend сервер запущен.');
  }
}

export async function getTickets(
  user_id?: string,
  status?: string,
  category?: string,
  queue?: string,
  limit: number = 50,
  offset: number = 0
): Promise<TicketListResponse> {
  const params = new URLSearchParams();
  if (user_id) params.append('user_id', user_id);
  if (status) params.append('status', status);
  if (category) params.append('category', category);
  if (queue) params.append('queue', queue);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());

  return apiRequest<TicketListResponse>(`/tickets?${params.toString()}`);
}

export async function getTicket(ticket_id: number): Promise<Ticket> {
  // Используем новый сгенерированный API
  const ticket: TicketResponse = await api.tickets.getById(ticket_id.toString());
  
  // Преобразуем новый тип в старый для обратной совместимости
  return {
    id: parseInt(ticket.id) || ticket_id,
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
}

export async function updateTicket(
  ticket_id: number,
  status?: string,
  priority?: string,
  category?: string,
  queue?: string,
  _comment?: string // Пока не используется в новом API
): Promise<Ticket> {
  // Используем новый сгенерированный API
  const updateData: TicketUpdate = {
    status: status as any, // Преобразуем строку в тип TicketStatus
    priority: priority as any, // Преобразуем строку в тип TicketPriority
    category_id: category || undefined,
    assigned_department_id: queue || undefined
  };
  
  const ticket: TicketResponse = await api.tickets.update(ticket_id.toString(), updateData);
  
  // Преобразуем новый тип в старый для обратной совместимости
  return {
    id: parseInt(ticket.id) || ticket_id,
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
}

export async function getComments(ticket_id: number): Promise<Comment[]> {
  return apiRequest<Comment[]>(`/tickets/${ticket_id}/comments`);
}

export async function addComment(
  ticket_id: number,
  comment_text: string,
  is_auto_reply: boolean = false
): Promise<Comment> {
  return apiRequest<Comment>(`/tickets/${ticket_id}/comments`, {
    method: 'POST',
    body: JSON.stringify({ comment_text, is_auto_reply }),
  });
}

export async function searchTickets(query: string, limit: number = 50, offset: number = 0) {
  const params = new URLSearchParams({ q: query, limit: limit.toString(), offset: offset.toString() });
  return apiRequest(`/tickets/search?${params.toString()}`);
}

export async function submitFeedback(ticket_id: number, rating: number, comment?: string): Promise<Feedback> {
  return apiRequest<Feedback>(`/tickets/${ticket_id}/feedback`, {
    method: 'POST',
    body: JSON.stringify({ rating, comment }),
  });
}

export async function getTemplates(category?: string): Promise<Template[]> {
  const params = category ? `?category=${category}` : '';
  return apiRequest<Template[]>(`/templates${params}`);
}

export const ticketExamples = [
  'Не могу войти в корпоративную почту, пишет неверный пароль.',
  'Нужно перенести отпуск в системе HR.',
  'Ошибка 500 в CRM при открытии карточки клиента.',
  'Хочу подключить новый проект в Jira.'
];

