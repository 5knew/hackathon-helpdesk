import jsPDF from 'jspdf';
import { Metrics, Ticket } from '../types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

// Функция для рендеринга текста с кириллицей в изображение и добавления в PDF
function addTextWithCyrillic(doc: jsPDF, text: string, x: number, y: number, fontSize: number = 12): number {
  // Создаем временный canvas для рендеринга текста
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    // Fallback: используем стандартный метод (может не отображать кириллицу)
    doc.setFontSize(fontSize);
    const lines = doc.splitTextToSize(text, 170);
    doc.text(lines, x, y);
    return lines.length * fontSize * 0.35;
  }
  
  // Устанавливаем шрифт с поддержкой кириллицы
  ctx.font = `${fontSize * 2.83}px Arial, "DejaVu Sans", sans-serif`; // 2.83 - коэффициент для конвертации мм в пиксели
  ctx.fillStyle = '#000000';
  ctx.textBaseline = 'top';
  
  // Разбиваем текст на строки
  const maxWidth = 170 * 2.83; // Максимальная ширина в пикселях
  const words = text.split(' ');
  const lines: string[] = [];
  let currentLine = '';
  
  words.forEach(word => {
    const testLine = currentLine ? `${currentLine} ${word}` : word;
    const metrics = ctx.measureText(testLine);
    
    if (metrics.width > maxWidth && currentLine) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = testLine;
    }
  });
  if (currentLine) {
    lines.push(currentLine);
  }
  
  // Рендерим каждую строку в изображение и добавляем в PDF
  let currentY = y;
  const lineHeight = fontSize * 0.35;
  
  lines.forEach((line) => {
    // Устанавливаем размер canvas для строки
    const textMetrics = ctx.measureText(line);
    canvas.width = Math.ceil(textMetrics.width) + 10;
    canvas.height = Math.ceil(fontSize * 2.83) + 10;
    
    // Очищаем canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.font = `${fontSize * 2.83}px Arial, "DejaVu Sans", sans-serif`;
    ctx.fillStyle = '#000000';
    ctx.textBaseline = 'top';
    
    // Рисуем текст
    ctx.fillText(line, 5, 5);
    
    // Конвертируем canvas в изображение и добавляем в PDF
    const imgData = canvas.toDataURL('image/png');
    doc.addImage(imgData, 'PNG', x, currentY, canvas.width / 2.83, canvas.height / 2.83);
    
    currentY += lineHeight;
  });
  
  return lines.length * lineHeight;
}

export function exportMetricsToPDF(metrics: Metrics, tickets: Ticket[] = []) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
    compress: true
  });
  
  let yPos = 20;
  
  // Заголовок
  yPos += addTextWithCyrillic(doc, 'Отчет по метрикам Helpdesk', 20, yPos, 20);
  yPos += 5;
  
  // Дата создания
  const dateStr = format(new Date(), 'dd MMMM yyyy, HH:mm', { locale: ru });
  yPos += addTextWithCyrillic(doc, `Дата создания: ${dateStr}`, 20, yPos, 12);
  yPos += 10;
  
  // Метрики
  yPos += addTextWithCyrillic(doc, 'Основные метрики', 20, yPos, 16);
  yPos += 8;
  
  yPos += addTextWithCyrillic(doc, `Автоматические решения: ${metrics.auto || 0}%`, 20, yPos, 12);
  yPos += 7;
  yPos += addTextWithCyrillic(doc, `Точность классификации: ${metrics.accuracy || 0}%`, 20, yPos, 12);
  yPos += 7;
  yPos += addTextWithCyrillic(doc, `Время ответа (SLA): ${metrics.sla || 0}%`, 20, yPos, 12);
  yPos += 7;
  yPos += addTextWithCyrillic(doc, `Очередь заявок: ${metrics.backlog || 0}`, 20, yPos, 12);
  yPos += 7;
  
  if (metrics.csat !== undefined && metrics.csat !== null) {
    yPos += addTextWithCyrillic(doc, `Удовлетворенность клиентов (CSAT): ${metrics.csat.toFixed(1)}%`, 20, yPos, 12);
    yPos += 7;
  }
  
  if (metrics.routing_error_rate !== undefined && metrics.routing_error_rate !== null) {
    yPos += addTextWithCyrillic(doc, `Ошибки маршрутизации: ${metrics.routing_error_rate.toFixed(1)}%`, 20, yPos, 12);
    yPos += 7;
  }
  
  yPos += 5;
  
  // Статистика по тикетам
  if (tickets.length > 0) {
    yPos += addTextWithCyrillic(doc, 'Статистика по заявкам', 20, yPos, 16);
    yPos += 8;
    
    const statusCounts = tickets.reduce((acc, ticket) => {
      const status = ticket.status || 'Unknown';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    // Переводим статусы на русский
    const statusTranslations: Record<string, string> = {
      'Open': 'Открыта',
      'In Progress': 'В работе',
      'Closed': 'Закрыта',
      'Pending': 'Ожидание',
      'Resolved': 'Решена'
    };
    
    Object.entries(statusCounts).forEach(([status, count]) => {
      const statusRu = statusTranslations[status] || status;
      yPos += addTextWithCyrillic(doc, `${statusRu}: ${count}`, 20, yPos, 12);
      yPos += 7;
    });
  }
  
  // Если контент не помещается, добавляем новую страницу
  if (yPos > 270) {
    doc.addPage();
    yPos = 20;
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

