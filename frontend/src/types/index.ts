export interface User {
  email: string;
  password: string;
}

export interface Metrics {
  auto: number;
  accuracy: number;
  sla: number;
  backlog: number;
}

export interface TicketResult {
  status: 'success' | 'warning';
  message: string;
}

export type ToastType = 'info' | 'success' | 'error';

