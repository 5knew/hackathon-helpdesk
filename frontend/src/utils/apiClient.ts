/**
 * Типизированный API клиент, сгенерированный из OpenAPI спецификации
 */

import type { paths, components } from '../types/api';
import { API_BASE_URL } from './apiConfig';
import { storage } from './storage';

// Типы для удобства
type HttpMethod = 'get' | 'post' | 'put' | 'delete' | 'patch';

// Упрощённые типы для опций запроса
interface RequestOptions {
  params?: Record<string, string | number>;
  query?: Record<string, any>;
  headers?: Record<string, string>;
  body?: any;
}

/**
 * Базовый класс для API клиента
 */
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Получить токен авторизации
   */
  private getAuthToken(): string | null {
    const user = storage.getUser();
    return user?.token || null;
  }

  /**
   * Универсальный метод для выполнения запросов
   */
  private async request<T = any>(
    path: string,
    method: HttpMethod,
    options?: RequestOptions
  ): Promise<T> {
    const url = new URL(path as string, this.baseUrl);
    
    // Добавляем query параметры
    if (options?.query) {
      Object.entries(options.query).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, String(value));
        }
      });
    }

    // Подставляем path параметры
    let finalPath = path as string;
    if (options?.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        finalPath = finalPath.replace(`{${key}}`, String(value));
      });
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };

    // Добавляем токен авторизации
    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      method: method.toUpperCase(),
      headers,
    };

    if (options?.body && (method === 'post' || method === 'put' || method === 'patch')) {
      config.body = JSON.stringify(options.body);
    }

    const response = await fetch(new URL(finalPath, this.baseUrl).toString(), config);

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      
      throw new Error(errorMessage);
    }

    // Если ответ пустой, возвращаем пустой объект
    const text = await response.text();
    if (!text) {
      return {} as T;
    }

    return JSON.parse(text) as T;
  }

  /**
   * GET запрос
   */
  async get<T = any>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, 'get', options);
  }

  /**
   * POST запрос
   */
  async post<T = any>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, 'post', options);
  }

  /**
   * PUT запрос
   */
  async put<T = any>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, 'put', options);
  }

  /**
   * DELETE запрос
   */
  async delete<T = any>(path: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(path, 'delete', options);
  }
}

// Экспортируем экземпляр клиента
export const apiClient = new ApiClient();

// Экспортируем типы для удобства использования
export type { components, paths };
export type TicketResponse = components['schemas']['TicketResponse'];
export type TicketCreate = components['schemas']['TicketCreate'];
export type TicketUpdate = components['schemas']['TicketUpdate'];
export type UserResponse = components['schemas']['UserResponse'];
export type UserRegister = components['schemas']['UserRegister'];
export type UserLogin = components['schemas']['UserLogin'];
export type TokenResponse = components['schemas']['TokenResponse'];
export type TicketStatus = components['schemas']['TicketStatus'];
export type TicketPriority = components['schemas']['TicketPriority'];
export type TicketSource = components['schemas']['TicketSource'];
export type TicketLanguage = components['schemas']['TicketLanguage'];
export type IssueType = components['schemas']['IssueType'];

