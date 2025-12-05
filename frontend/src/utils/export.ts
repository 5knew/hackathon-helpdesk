import jsPDF from 'jspdf';
import { Metrics, Ticket } from '../types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

export function exportMetricsToPDF(metrics: Metrics, tickets: Ticket[] = []) {
  const doc = new jsPDF();
  
  // Заголовок
  doc.setFontSize(20);
  doc.text('Отчет по метрикам Helpdesk', 20, 20);
  
  doc.setFontSize(12);
  doc.text(`Дата создания: ${format(new Date(), 'dd MMMM yyyy, HH:mm', { locale: ru })}`, 20, 30);
  
  let yPos = 40;
  
  // Метрики
  doc.setFontSize(16);
  doc.text('Основные метрики', 20, yPos);
  yPos += 10;
  
  doc.setFontSize(12);
  doc.text(`Автоматические решения: ${metrics.auto}%`, 20, yPos);
  yPos += 7;
  doc.text(`Точность классификации: ${metrics.accuracy}%`, 20, yPos);
  yPos += 7;
  doc.text(`Время ответа (SLA): ${metrics.sla}%`, 20, yPos);
  yPos += 7;
  doc.text(`Очередь заявок: ${metrics.backlog}`, 20, yPos);
  yPos += 7;
  
  if (metrics.csat) {
    doc.text(`Удовлетворенность клиентов (CSAT): ${metrics.csat.toFixed(1)}%`, 20, yPos);
    yPos += 7;
  }
  
  if (metrics.routing_error_rate !== undefined) {
    doc.text(`Ошибки маршрутизации: ${metrics.routing_error_rate.toFixed(1)}%`, 20, yPos);
    yPos += 7;
  }
  
  yPos += 5;
  
  // Статистика по тикетам
  if (tickets.length > 0) {
    doc.setFontSize(16);
    doc.text('Статистика по заявкам', 20, yPos);
    yPos += 10;
    
    const statusCounts = tickets.reduce((acc, ticket) => {
      acc[ticket.status] = (acc[ticket.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    doc.setFontSize(12);
    Object.entries(statusCounts).forEach(([status, count]) => {
      doc.text(`${status}: ${count}`, 20, yPos);
      yPos += 7;
    });
  }
  
  // Сохранение
  doc.save(`metrics-report-${format(new Date(), 'yyyy-MM-dd')}.pdf`);
}

export function exportTicketsToCSV(tickets: Ticket[]) {
  const headers = ['ID', 'Тема', 'Статус', 'Категория', 'Приоритет', 'Дата создания', 'Дата закрытия'];
  const rows = tickets.map(ticket => [
    ticket.id.toString(),
    ticket.subject,
    ticket.status,
    ticket.category,
    ticket.priority,
    format(new Date(ticket.created_at), 'yyyy-MM-dd HH:mm'),
    ticket.closed_at ? format(new Date(ticket.closed_at), 'yyyy-MM-dd HH:mm') : ''
  ]);
  
  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
  ].join('\n');
  
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `tickets-${format(new Date(), 'yyyy-MM-dd')}.csv`;
  link.click();
}

