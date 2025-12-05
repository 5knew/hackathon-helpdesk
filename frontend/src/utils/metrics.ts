import { Metrics } from '../types';

// Backend API URL (Core API, не ML сервис)
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002';

export async function fetchMetrics(): Promise<Metrics> {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Преобразуем данные из API в формат Metrics
    return {
      auto: data.auto_resolution_rate || 0,
      accuracy: data.accuracy_metrics?.avg_confidence || 0,
      sla: Math.min(99, 100 - (data.avg_response_time || 0) * 10), // Преобразуем время ответа в SLA
      backlog: data.total_tickets - data.closed_tickets || 0
    };
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

