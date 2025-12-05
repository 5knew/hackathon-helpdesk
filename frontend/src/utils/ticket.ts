import { TicketResult, Ticket, TicketListResponse, Comment, Feedback, Template } from '../types';
import { storage } from './storage';
import { apiRequest } from './apiConfig';

export async function submitTicketToAPI(text: string): Promise<TicketResult> {
  const user = storage.getUser();
  const userEmail = user?.email || 'guest@user.com';
  
  // Разделяем текст на subject и body (если есть перенос строки)
  const lines = text.split('\n');
  const subject = lines[0].substring(0, 100) || 'Заявка';
  const body = text;

  try {
    const data = await apiRequest<any>('/submit_ticket', {
      method: 'POST',
      body: JSON.stringify({
        user_id: userEmail,
        problem_description: body,
        subject: subject,
        language: 'ru' // Можно добавить переключатель языка
      }),
    });
    
    // Определяем статус на основе результата
    const isAutoClosed = data.status === 'Closed' || data.queue === 'Automated';
    
    return {
      status: isAutoClosed ? 'success' : 'warning',
      message: data.message || 'Заявка обработана',
      needs_clarification: data.needs_clarification || false,
      confidence_warning: data.confidence_warning || undefined,
      queue: data.queue || undefined
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
  return apiRequest<Ticket>(`/tickets/${ticket_id}`);
}

export async function updateTicket(
  ticket_id: number,
  status?: string,
  priority?: string,
  category?: string,
  queue?: string,
  comment?: string
): Promise<Ticket> {
  return apiRequest<Ticket>(`/tickets/${ticket_id}`, {
    method: 'PUT',
    body: JSON.stringify({ status, priority, category, queue, comment }),
  });
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

