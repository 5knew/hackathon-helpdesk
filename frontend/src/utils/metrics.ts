import { Metrics } from '../types';

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

