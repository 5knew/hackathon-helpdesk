/**
 * Конфигурация API для связи frontend с backend
 */
import { storage } from './storage';

// Базовый URL backend API
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

// ML Service URL (если нужен)
export const ML_SERVICE_URL = import.meta.env.VITE_ML_SERVICE_URL || 'http://localhost:8000';

/**
 * Проверка доступности backend API
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.ok;
  } catch (error) {
    console.error('Backend API недоступен:', error);
    return false;
  }
}

/**
 * Универсальная функция для API запросов с обработкой ошибок
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Получаем токен из storage
  const token = storage.getToken();
  
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Добавляем токен авторизации, если есть
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    
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
  } catch (error) {
    if (error instanceof Error) {
      console.error(`API Error [${endpoint}]:`, error.message);
      throw error;
    }
    throw new Error(`Неизвестная ошибка при запросе к ${endpoint}`);
  }
}


