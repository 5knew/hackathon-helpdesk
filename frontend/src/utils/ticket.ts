import { TicketResult } from '../types';
import { storage } from './storage';

// Backend API URL (Core API, не ML сервис)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export async function submitTicketToAPI(text: string): Promise<TicketResult> {
  const user = storage.getUser();
  const userEmail = user?.email || 'guest@user.com';
  
  // Разделяем текст на subject и body (если есть перенос строки)
  const lines = text.split('\n');
  const subject = lines[0].substring(0, 100) || 'Заявка';
  const body = text;

  try {
    const response = await fetch(`${API_BASE_URL}/submit_ticket`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userEmail,
        problem_description: body,
        subject: subject,
        language: 'ru' // Можно добавить переключатель языка
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
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

export const ticketExamples = [
  'Не могу войти в корпоративную почту, пишет неверный пароль.',
  'Нужно перенести отпуск в системе HR.',
  'Ошибка 500 в CRM при открытии карточки клиента.',
  'Хочу подключить новый проект в Jira.'
];

