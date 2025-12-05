import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Chip } from '../components/Chip';
import { Metrics, TicketResult } from '../types';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { fetchMetrics } from '../utils/metrics';
import { submitTicketToAPI, ticketExamples } from '../utils/ticket';
import { exportMetricsToPDF } from '../utils/export';
import { api } from '../utils/apiGenerated';
import { useLanguage } from '../contexts/LanguageContext';
import { NotificationsPanel } from '../components/NotificationsPanel';

export const Dashboard: React.FC = () => {
  const { t } = useLanguage();
  const [ticketText, setTicketText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [ticketResult, setTicketResult] = useState<TicketResult | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [userEmail, setUserEmail] = useState('demo@user');
  const [newTicketsCount, setNewTicketsCount] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }

    const user = storage.getUser();
    if (user?.email) {
      setUserEmail(user.email);
    }

    loadMetrics();
    loadNewTicketsCount();
  }, [navigate]);

  const loadNewTicketsCount = async () => {
    try {
      // Используем новый сгенерированный API
      const tickets = await api.tickets.list({ 
        status: 'in_work' // Статусы: 'new' | 'auto_resolved' | 'in_work' | 'waiting' | 'closed'
      });
      setNewTicketsCount(tickets.length);
    } catch (error) {
      // Игнорируем ошибки
    }
  };

  const handleLogout = () => {
    storage.setLogged(false);
    navigate('/');
  };

  const handleSubmitTicket = async () => {
    const trimmedText = ticketText.trim();

    if (!trimmedText) {
      showToast(t('dashboard.ticket.text_label'), 'error');
      return;
    }

    setIsSubmitting(true);
    setTicketResult(null);

    try {
      const result = await submitTicketToAPI(trimmedText);
      setTicketResult(result);
      loadNewTicketsCount(); // Обновляем счетчик новых заявок
    } catch (error) {
      showToast(t('error.submit_ticket'), 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClearTicket = () => {
    setTicketText('');
    setTicketResult(null);
  };

  const handlePrefillTicket = () => {
    const example = ticketExamples[Math.floor(Math.random() * ticketExamples.length)];
    setTicketText(example);
  };

  const loadMetrics = async () => {
    try {
      const newMetrics = await fetchMetrics();
      setMetrics(newMetrics);
      showToast(t('error.metrics_updated'), 'success');
    } catch (error) {
      console.error('Error loading metrics:', error);
      showToast(t('error.load_metrics'), 'error');
    }
  };

  const handleExportMetrics = async () => {
    try {
      // Используем новый сгенерированный API
      const tickets = await api.tickets.list();
      if (metrics) {
        // Преобразуем новые типы в старые для обратной совместимости
        const oldTickets = tickets.map(t => ({
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
        exportMetricsToPDF(metrics, oldTickets);
        showToast(t('analytics.export_success'), 'success');
      }
    } catch (error) {
      showToast('Ошибка экспорта', 'error');
    }
  };

  const setMetricValue = (key: keyof Metrics, value: number) => {
    if (key === 'backlog') {
      const element = document.getElementById('backlogValue');
      const bar = document.getElementById('backlogBar');
      if (element) element.innerText = `${value} заявок`;
      if (bar) bar.style.width = `${Math.min(value * 3, 100)}%`;
      return;
    }

    const percentElement = document.getElementById(`${key}Percent`);
    const heroElement = document.getElementById(`${key}PercentHero`);
    const barElement = document.getElementById(`${key}Bar`);

    if (percentElement) percentElement.innerText = `${value}%`;
    if (heroElement) heroElement.innerText = `${value}%`;
    if (barElement) barElement.style.width = `${value}%`;
  };

  useEffect(() => {
    if (metrics) {
      setMetricValue('auto', metrics.auto);
      setMetricValue('accuracy', metrics.accuracy);
      setMetricValue('sla', metrics.sla);
      setMetricValue('backlog', metrics.backlog);
    }
  }, [metrics]);

  return (
    <div className="page-shell">
      <header className="topbar card glass">
        <div className="brand">
          <div className="logo-dot"></div>
          <div>
            <p className="brand-name">{t('app.name')}</p>
            <span className="brand-sub">{t('dashboard.title')}</span>
          </div>
        </div>
        <div className="topbar-actions">
          <Link to="/tickets" className="ghost" style={{ position: 'relative', marginRight: '12px' }}>
            {t('nav.tickets')}
            {newTicketsCount > 0 && (
              <span
                style={{
                  position: 'absolute',
                  top: '-8px',
                  right: '-8px',
                  background: '#dc3545',
                  color: 'white',
                  borderRadius: '50%',
                  width: '20px',
                  height: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75em',
                  fontWeight: 'bold'
                }}
              >
                {newTicketsCount > 9 ? '9+' : newTicketsCount}
              </span>
            )}
          </Link>
          <Link to="/analytics" className="ghost" style={{ marginRight: '12px' }}>
            {t('nav.analytics')}
          </Link>
          <Link to="/settings" className="ghost" style={{ marginRight: '12px' }}>
            {t('nav.settings')}
          </Link>
          <NotificationsPanel />
          <div className="chip ghost">{userEmail}</div>
          <button className="ghost" onClick={handleLogout}>
            {t('common.logout')}
          </button>
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="card hero-card">
          <div>
            <div className="eyebrow">{t('dashboard.hero.eyebrow')}</div>
            <h1>{t('dashboard.hero.title')}</h1>
            <p className="muted">
              {t('dashboard.hero.desc')}
            </p>
            <div className="chips">
              <Chip variant="success">Live demo</Chip>
              <Chip variant="ghost">/submit_ticket</Chip>
              <Chip variant="ghost">/metrics</Chip>
            </div>
          </div>
          <div className="hero-metrics">
            <div className="hero-metric">
              <p className="label">{t('dashboard.metrics.auto_resolutions')}</p>
              <p className="stat" id="autoPercentHero">
                —
              </p>
            </div>
            <div className="hero-metric">
              <p className="label">{t('dashboard.metrics.ai_accuracy')}</p>
              <p className="stat" id="accuracyPercentHero">
                —
              </p>
            </div>
          </div>
        </section>

        <section className="card ticket-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">{t('dashboard.ticket.title')}</p>
              <h3>{t('dashboard.ticket.label')}</h3>
              <p className="muted">{t('dashboard.ticket.desc')}</p>
            </div>
            <button className="ghost" onClick={handleClearTicket}>
              {t('common.clear')}
            </button>
          </div>
          <div className="field">
            <label htmlFor="ticketText">{t('dashboard.ticket.text_label')}</label>
            <textarea
              id="ticketText"
              placeholder={t('dashboard.ticket.placeholder')}
              rows={5}
              value={ticketText}
              onChange={(e) => setTicketText(e.target.value)}
            />
          </div>
          <div className="actions">
            <button className="secondary" onClick={handlePrefillTicket}>
              {t('dashboard.ticket.fill_example')}
            </button>
            <button className="primary" id="submitBtn" onClick={handleSubmitTicket} disabled={isSubmitting}>
              {isSubmitting ? t('common.submitting') : t('common.submit')}
            </button>
          </div>
          <div className="result-wrapper">
            <p className="label">{t('dashboard.ticket.result')}</p>
            <div
              className={`result-box ${ticketResult ? 'show' : ''} ${isSubmitting ? 'pending' : ''}`}
              data-status={ticketResult?.status || ''}
            >
              {isSubmitting ? (
                <>
                  <div className="loader"></div>
                  <p>{t('dashboard.ticket.analyzing')}</p>
                </>
              ) : ticketResult ? (
                <>
                  {ticketResult.message}
                  {ticketResult.needs_clarification && (
                    <div style={{ marginTop: '8px', padding: '8px', background: '#fff3cd', borderRadius: '4px', fontSize: '0.9em' }}>
                      ⚠️ {t('dashboard.ticket.needs_clarification')}: {ticketResult.confidence_warning}
                    </div>
                  )}
                  {ticketResult.queue && (
                    <div style={{ marginTop: '4px', fontSize: '0.85em', color: '#666' }}>
                      {t('dashboard.ticket.queue')}: {ticketResult.queue}
                    </div>
                  )}
                </>
              ) : (
                t('dashboard.ticket.no_result')
              )}
            </div>
          </div>
        </section>

        <section className="card metrics-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">{t('dashboard.metrics.title')}</p>
              <h3>{t('dashboard.metrics.subtitle')}</h3>
              <p className="muted">{t('dashboard.metrics.desc')}</p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="secondary" onClick={handleExportMetrics}>
                {t('dashboard.export.pdf')}
              </button>
              <button className="ghost" onClick={loadMetrics}>
                {t('common.update')}
              </button>
            </div>
          </div>

          <div className="metric-grid">
            <div className="metric-tile">
              <div className="metric-top">
                <p>{t('dashboard.metrics.auto')}</p>
                <span className="pill success">AI</span>
              </div>
              <p className="metric-value" id="autoPercent">
                —
              </p>
              <div className="progress">
                <div id="autoBar" className="progress-bar"></div>
              </div>
            </div>

            <div className="metric-tile">
              <div className="metric-top">
                <p>{t('dashboard.metrics.accuracy')}</p>
                <span className="pill info">ML</span>
              </div>
              <p className="metric-value" id="accuracyPercent">
                —
              </p>
              <div className="progress">
                <div id="accuracyBar" className="progress-bar"></div>
              </div>
            </div>

            <div className="metric-tile">
              <div className="metric-top">
                <p>{t('dashboard.metrics.sla')}</p>
                <span className="pill warning">SLA</span>
              </div>
              <p className="metric-value" id="slaPercent">
                —
              </p>
              <div className="progress">
                <div id="slaBar" className="progress-bar"></div>
              </div>
            </div>

            <div className="metric-tile">
              <div className="metric-top">
                <p>{t('dashboard.metrics.backlog')}</p>
                <span className="pill neutral">OPS</span>
              </div>
              <p className="metric-value" id="backlogValue">
                —
              </p>
              <div className="progress">
                <div id="backlogBar" className="progress-bar"></div>
              </div>
            </div>

            {metrics?.csat && (
              <div className="metric-tile">
                <div className="metric-top">
                  <p>{t('dashboard.metrics.csat')}</p>
                  <span className="pill success">CSAT</span>
                </div>
                <p className="metric-value" id="csatPercent">
                  {metrics.csat.toFixed(1)}%
                </p>
                <div className="progress">
                  <div id="csatBar" className="progress-bar" style={{ width: `${metrics.csat}%` }}></div>
                </div>
              </div>
            )}

            {metrics?.routing_error_rate !== undefined && (
              <div className="metric-tile">
                <div className="metric-top">
                  <p>{t('dashboard.metrics.routing_errors')}</p>
                  <span className="pill warning">ERR</span>
                </div>
                <p className="metric-value" id="routingErrorPercent">
                  {metrics.routing_error_rate.toFixed(1)}%
                </p>
                <div className="progress">
                  <div id="routingErrorBar" className="progress-bar" style={{ width: `${metrics.routing_error_rate}%`, background: '#dc3545' }}></div>
                </div>
                {metrics.routing_errors && (
                  <div style={{ marginTop: '8px', fontSize: '0.75em', color: '#666' }}>
                    {t('dashboard.metrics.manual_review')}: {metrics.routing_errors.manual_review || 0} | 
                    {t('dashboard.metrics.low_confidence')}: {metrics.routing_errors.low_confidence || 0}
                  </div>
                )}
              </div>
            )}
          </div>

          {metrics?.trends && Object.keys(metrics.trends).length > 0 && (
            <div style={{ marginTop: '24px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
              <h4 style={{ marginBottom: '12px', fontSize: '0.9em' }}>Тренды за 7 дней</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '8px', fontSize: '0.75em' }}>
                {Object.entries(metrics.trends).reverse().map(([date, data]) => (
                  <div key={date} style={{ textAlign: 'center', padding: '8px', background: 'white', borderRadius: '4px' }}>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{new Date(date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}</div>
                    <div>Всего: {data.total}</div>
                    <div style={{ color: '#28a745' }}>Закрыто: {data.closed}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
};

