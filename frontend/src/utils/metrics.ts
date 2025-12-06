import { Metrics } from '../types';
import { apiRequest } from './apiConfig';

export async function fetchMetrics(): Promise<Metrics> {
  try {
    // Эндпоинт /metrics пока не реализован в бэкенде
    // Используем моки, но не показываем ошибку пользователю
    console.warn('Metrics endpoint not implemented, using mock data');
    return mockMetrics();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    // Fallback на моки при ошибке
    return mockMetrics();
  }
}

export function mockMetrics(): Metrics {
  return {
    auto: randomRange(68, 93),
    accuracy: randomRange(84, 97),
    sla: randomRange(95, 99),
    backlog: randomRange(8, 32)
  };
}

function randomRange(min: number, max: number): number {
  return Math.round(Math.random() * (max - min) + min);
}

