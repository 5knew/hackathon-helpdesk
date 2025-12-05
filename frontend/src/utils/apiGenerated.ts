/**
 * Сгенерированные API методы на основе OpenAPI спецификации
 * Этот файл предоставляет удобные обёртки для работы с API
 */

import { apiClient, type TicketResponse, type TicketCreate, type TicketUpdate, type UserRegister, type UserLogin, type TokenResponse, type UserResponse } from './apiClient';

// Реэкспортируем типы для удобства использования
export type { TicketResponse, TicketCreate, TicketUpdate, UserRegister, UserLogin, TokenResponse, UserResponse };

/**
 * API для аутентификации
 */
export const authApi = {
  /**
   * Регистрация нового пользователя
   */
  async register(data: UserRegister): Promise<UserResponse> {
    return apiClient.post('/auth/register', {
      body: data,
    });
  },

  /**
   * Вход пользователя
   */
  async login(data: UserLogin): Promise<TokenResponse> {
    return apiClient.post('/auth/login', {
      body: data,
    });
  },

  /**
   * Получить информацию о текущем пользователе
   */
  async getCurrentUser(): Promise<UserResponse> {
    return apiClient.get('/auth/me');
  },

  /**
   * Выход пользователя
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  },
};

/**
 * API для работы с тикетами
 */
export const ticketsApi = {
  /**
   * Создать новый тикет
   */
  async create(data: TicketCreate): Promise<TicketResponse> {
    return apiClient.post('/tickets/create', {
      body: data,
    });
  },

  /**
   * Получить список тикетов
   */
  async list(params?: {
    skip?: number;
    limit?: number;
    status?: 'new' | 'auto_resolved' | 'in_work' | 'waiting' | 'closed';
  }): Promise<TicketResponse[]> {
    return apiClient.get('/tickets', {
      query: params,
    });
  },

  /**
   * Получить тикет по ID
   */
  async getById(ticketId: string): Promise<TicketResponse> {
    return apiClient.get('/tickets/{ticket_id}', {
      params: { ticket_id: ticketId },
    });
  },

  /**
   * Обновить тикет
   */
  async update(ticketId: string, data: TicketUpdate): Promise<TicketResponse> {
    return apiClient.put('/tickets/{ticket_id}', {
      params: { ticket_id: ticketId },
      body: data,
    });
  },

  /**
   * Удалить тикет (soft delete)
   */
  async delete(ticketId: string): Promise<void> {
    await apiClient.delete('/tickets/{ticket_id}', {
      params: { ticket_id: ticketId },
    });
  },
};

/**
 * Health check
 */
export const healthApi = {
  /**
   * Проверить здоровье API
   */
  async check(): Promise<unknown> {
    return apiClient.get('/health');
  },
};

// Экспортируем все API методы
export const api = {
  auth: authApi,
  tickets: ticketsApi,
  health: healthApi,
};

