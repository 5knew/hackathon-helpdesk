import { TicketResult } from '../types';

export function submitTicketToAPI(text: string): Promise<TicketResult> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const departments = ['IT', 'HR', 'Финансы', 'Техподдержка'];
      const isAuto = text.toLowerCase().includes('пароль') || text.toLowerCase().includes('войти');
      const dept = departments[Math.floor(Math.random() * departments.length)];

      if (isAuto) {
        resolve({
          status: 'success',
          message: 'Запрос закрыт автоматически (AI)'
        });
      } else {
        resolve({
          status: 'warning',
          message: `Передано в отдел: ${dept}`
        });
      }
    }, 1300);
  });
}

export const ticketExamples = [
  'Не могу войти в корпоративную почту, пишет неверный пароль.',
  'Нужно перенести отпуск в системе HR.',
  'Ошибка 500 в CRM при открытии карточки клиента.',
  'Хочу подключить новый проект в Jira.'
];

