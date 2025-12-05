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

