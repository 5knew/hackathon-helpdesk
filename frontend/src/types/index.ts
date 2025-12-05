export interface User {
  email: string;
  password: string;
}

export interface Metrics {
  auto: number;
  accuracy: number;
  sla: number;
  backlog: number;
  csat?: number; // Customer Satisfaction Score
  routing_error_rate?: number; // Процент ошибок маршрутизации
  routing_errors?: {
    manual_review?: number;
    low_confidence?: number;
    needs_clarification?: number;
  };
  avg_resolution_time_by_category?: Record<string, number>; // Время обработки по категориям
  trends?: Record<string, { total: number; closed: number }>; // Тренды за 7 дней
}

export interface TicketResult {
  status: 'success' | 'warning';
  message: string;
  needs_clarification?: boolean; // Требуется уточнение
  confidence_warning?: string; // Предупреждение о низкой уверенности
  queue?: string; // Очередь, в которую направлен тикет
}

export type ToastType = 'info' | 'success' | 'error';

// Расширенные типы для новой функциональности
export interface Ticket {
  id: number;
  user_id: string;
  subject: string;
  problem_description: string;
  status: 'Open' | 'In Progress' | 'Closed' | 'Waiting';
  category: string;
  priority: 'Низкий' | 'Средний' | 'Высокий';
  problem_type: 'Типовой' | 'Сложный';
  queue: string;
  created_at: string;
  updated_at: string;
  closed_at?: string;
  auto_closed?: boolean;
  sla_deadline?: string;
  csat_score?: number;
  csat_comment?: string;
}

export interface Comment {
  id: number;
  ticket_id: number;
  author: string;
  author_type: 'user' | 'operator' | 'system';
  text: string;
  created_at: string;
  is_auto_reply?: boolean;
}

export interface TicketHistory {
  id: number;
  ticket_id: number;
  action: string;
  changed_by: string;
  old_value?: string;
  new_value?: string;
  created_at: string;
}

export interface TicketFilter {
  status?: string[];
  category?: string[];
  priority?: string[];
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export interface Template {
  id: number;
  name: string;
  category: string;
  text: string;
  language: 'ru' | 'kz';
}

export interface Integration {
  id: string;
  name: string;
  type: 'email' | 'slack' | 'telegram' | 'webhook';
  enabled: boolean;
  last_sync?: string;
  config?: Record<string, any>;
}

export type Language = 'ru' | 'kz' | 'en';

