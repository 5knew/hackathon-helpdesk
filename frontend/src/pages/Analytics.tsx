import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Metrics, Ticket } from '../types';
import { fetchMetrics } from '../utils/metrics';
import { api } from '../utils/apiGenerated';
import { exportMetricsToPDF, exportTicketsToCSV } from '../utils/export';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { format, subDays } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useLanguage } from '../contexts/LanguageContext';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

export const Analytics: React.FC = () => {
  const { t } = useLanguage();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState(7);
  const navigate = useNavigate();

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }
    loadData();
  }, [navigate, dateRange]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Используем новый сгенерированный API
      const [metricsData, ticketsData] = await Promise.all([
        fetchMetrics(),
        api.tickets.list()
      ]);
      setMetrics(metricsData);
      // Преобразуем новые типы в старые для обратной совместимости
      const oldTickets: Ticket[] = ticketsData.map(t => ({
        id: parseInt(t.id) || 0,
        user_id: t.user_id,
        problem_description: t.body,
        status: t.status,
        category: t.category_id || '',
        priority: t.priority || '',
        queue: t.assigned_department_id || '',
        problem_type: t.issue_type || '',
        needs_clarification: false,
        subject: t.subject || '',
        created_at: t.created_at,
        updated_at: t.updated_at,
        closed_at: t.closed_at || undefined
      }));
      setTickets(oldTickets);
    } catch (error) {
      showToast(t('analytics.load_error'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPDF = () => {
    if (metrics) {
      exportMetricsToPDF(metrics, tickets);
      showToast(t('analytics.export_success'), 'success');
    }
  };

  const handleExportCSV = () => {
    exportTicketsToCSV(tickets);
    showToast(t('analytics.csv_success'), 'success');
  };

  // Подготовка данных для графиков
  const categoryData = tickets.reduce((acc, ticket) => {
    acc[ticket.category] = (acc[ticket.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const categoryChartData = Object.entries(categoryData).map(([name, value]) => ({
    name,
    value
  }));

  const statusData = tickets.reduce((acc, ticket) => {
    acc[ticket.status] = (acc[ticket.status] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const statusChartData = Object.entries(statusData).map(([name, value]) => ({
    name: name === 'Open' ? 'Открыта' : name === 'In Progress' ? 'В работе' : name === 'Closed' ? 'Закрыта' : 'Ожидание',
    value
  }));

  // Тренды по дням
  const trendsData = Array.from({ length: dateRange }, (_, i) => {
    const date = subDays(new Date(), dateRange - i - 1);
    const dateStr = format(date, 'yyyy-MM-dd');
    const dayTickets = tickets.filter(t => format(new Date(t.created_at), 'yyyy-MM-dd') === dateStr);
    return {
      date: format(date, 'dd.MM'),
      total: dayTickets.length,
      closed: dayTickets.filter(t => t.status === 'Closed').length,
      open: dayTickets.filter(t => t.status === 'Open').length
    };
  });

  // Heatmap активности по часам
  const heatmapData = Array.from({ length: 24 }, (_, hour) => {
    const hourTickets = tickets.filter(t => {
      const ticketHour = new Date(t.created_at).getHours();
      return ticketHour === hour;
    });
    return {
      hour: `${hour}:00`,
      count: hourTickets.length
    };
  });

  if (loading) {
    return (
      <div className="page-shell">
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <div className="loader"></div>
          <p className="muted">{t('analytics.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-shell">
      <header className="topbar card glass">
        <div className="brand">
          <div className="logo-dot"></div>
          <div>
            <p className="brand-name">{t('app.name')}</p>
            <span className="brand-sub">{t('analytics.subtitle')}</span>
          </div>
        </div>
        <div className="topbar-actions">
          <Link to="/dashboard" className="ghost" style={{ marginRight: '12px' }}>
            {t('nav.dashboard')}
          </Link>
          <Link to="/tickets" className="ghost" style={{ marginRight: '12px' }}>
            {t('nav.tickets')}
          </Link>
          <button className="ghost" onClick={() => { storage.setLogged(false); navigate('/'); }}>
            {t('common.logout')}
          </button>
        </div>
      </header>

      <main style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto' }}>
        <div className="card" style={{ marginBottom: '24px' }}>
          <div className="section-head">
            <div>
              <h1>{t('analytics.advanced')}</h1>
              <p className="muted">{t('analytics.desc')}</p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(Number(e.target.value))}
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd' }}
              >
                <option value={7}>7 {t('analytics.days')}</option>
                <option value={14}>14 {t('analytics.days')}</option>
                <option value={30}>30 {t('analytics.days')}</option>
                <option value={90}>90 {t('analytics.days')}</option>
              </select>
              <button className="secondary" onClick={handleExportCSV}>
                {t('analytics.export.csv')}
              </button>
              <button className="primary" onClick={handleExportPDF}>
                {t('analytics.export.pdf')}
              </button>
            </div>
          </div>
        </div>

        {/* График трендов */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0' }}>{t('analytics.trends')} {dateRange} {t('analytics.days')}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="total" stroke="#0088FE" name={t('analytics.total')} />
              <Line type="monotone" dataKey="closed" stroke="#00C49F" name={t('analytics.closed')} />
              <Line type="monotone" dataKey="open" stroke="#FF8042" name={t('analytics.open')} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
          {/* Распределение по категориям */}
          <div className="card">
            <h2 style={{ margin: '0 0 16px 0' }}>{t('analytics.category_distribution')}</h2>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Распределение по статусам */}
          <div className="card">
            <h2 style={{ margin: '0 0 16px 0' }}>{t('analytics.status_distribution')}</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={statusChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Heatmap активности */}
        <div className="card">
          <h2 style={{ margin: '0 0 16px 0' }}>{t('analytics.activity_heatmap')}</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={heatmapData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#00C49F" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Метрики по категориям */}
        {metrics?.avg_resolution_time_by_category && (
          <div className="card" style={{ marginTop: '24px' }}>
            <h2 style={{ margin: '0 0 16px 0' }}>{t('analytics.avg_resolution_time')}</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {Object.entries(metrics.avg_resolution_time_by_category).map(([category, hours]) => (
                <div key={category} style={{ padding: '12px', background: '#f8f9fa', borderRadius: '6px' }}>
                  <p style={{ margin: '0 0 4px 0', fontWeight: 'bold' }}>{category}</p>
                  <p style={{ margin: 0, fontSize: '1.2em', color: '#007bff' }}>{hours.toFixed(1)} ч</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

