import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrandBar } from '../components/BrandBar';
import { Chip } from '../components/Chip';
import { Metrics, TicketResult } from '../types';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { fetchMetrics } from '../utils/metrics';
import { submitTicketToAPI, ticketExamples } from '../utils/ticket';

export const Dashboard: React.FC = () => {
  const [ticketText, setTicketText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [ticketResult, setTicketResult] = useState<TicketResult | null>(null);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [userEmail, setUserEmail] = useState('demo@user');
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
  }, [navigate]);

  const handleLogout = () => {
    storage.setLogged(false);
    navigate('/');
  };

  const handleSubmitTicket = async () => {
    const trimmedText = ticketText.trim();

    if (!trimmedText) {
      showToast('Введите текст заявки', 'error');
      return;
    }

    setIsSubmitting(true);
    setTicketResult(null);

    try {
      const result = await submitTicketToAPI(trimmedText);
      setTicketResult(result);
    } catch (error) {
      showToast('Ошибка при отправке заявки', 'error');
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
      showToast('Метрики обновлены', 'success');
    } catch (error) {
      console.error('Error loading metrics:', error);
      showToast('Ошибка загрузки метрик', 'error');
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
            <p className="brand-name">AI AutoResponder</p>
            <span className="brand-sub">Панель мониторинга</span>
          </div>
        </div>
        <div className="topbar-actions">
          <div className="chip ghost">{userEmail}</div>
          <button className="ghost" onClick={handleLogout}>
            Выйти
          </button>
        </div>
      </header>

      <main className="dashboard-grid">
        <section className="card hero-card">
          <div>
            <div className="eyebrow">Единый вход • Мониторинг</div>
            <h1>Отправляйте заявки и мгновенно видьте результат работы AI.</h1>
            <p className="muted">
              Имитация Core API: отправляем обращение, показываем статус ("закрыто автоматически" или "передано в
              отдел") и метрики качества.
            </p>
            <div className="chips">
              <Chip variant="success">Live demo</Chip>
              <Chip variant="ghost">/submit_ticket</Chip>
              <Chip variant="ghost">/metrics</Chip>
            </div>
          </div>
          <div className="hero-metrics">
            <div className="hero-metric">
              <p className="label">Авто-решений</p>
              <p className="stat" id="autoPercentHero">
                —
              </p>
            </div>
            <div className="hero-metric">
              <p className="label">Точность AI</p>
              <p className="stat" id="accuracyPercentHero">
                —
              </p>
            </div>
          </div>
        </section>

        <section className="card ticket-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Новая заявка</p>
              <h3>Опишите проблему</h3>
              <p className="muted">Текст отправится на Core API (имитация). Возвратим статус обработки.</p>
            </div>
            <button className="ghost" onClick={handleClearTicket}>
              Очистить
            </button>
          </div>
          <div className="field">
            <label htmlFor="ticketText">Текст заявки</label>
            <textarea
              id="ticketText"
              placeholder="Например: Не получается войти в корпоративную почту"
              rows={5}
              value={ticketText}
              onChange={(e) => setTicketText(e.target.value)}
            />
          </div>
          <div className="actions">
            <button className="secondary" onClick={handlePrefillTicket}>
              Заполнить пример
            </button>
            <button className="primary" id="submitBtn" onClick={handleSubmitTicket} disabled={isSubmitting}>
              {isSubmitting ? 'Отправляем...' : 'Отправить'}
            </button>
          </div>
          <div className="result-wrapper">
            <p className="label">Результат обработки</p>
            <div
              className={`result-box ${ticketResult ? 'show' : ''} ${isSubmitting ? 'pending' : ''}`}
              data-status={ticketResult?.status || ''}
            >
              {isSubmitting ? (
                <>
                  <div className="loader"></div>
                  <p>AI анализирует заявку...</p>
                </>
              ) : ticketResult ? (
                ticketResult.message
              ) : (
                'Пока нет результата'
              )}
            </div>
          </div>
        </section>

        <section className="card metrics-card">
          <div className="section-head">
            <div>
              <p className="eyebrow">Мониторинг</p>
              <h3>Метрики качества</h3>
              <p className="muted">Данные из /metrics (имитация). Нажмите «Обновить», чтобы пересчитать.</p>
            </div>
            <button className="ghost" onClick={loadMetrics}>
              Обновить
            </button>
          </div>

          <div className="metric-grid">
            <div className="metric-tile">
              <div className="metric-top">
                <p>Автоматические решения</p>
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
                <p>Точность классификации</p>
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
                <p>Время ответа</p>
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
                <p>Очередь заявок</p>
                <span className="pill neutral">OPS</span>
              </div>
              <p className="metric-value" id="backlogValue">
                —
              </p>
              <div className="progress">
                <div id="backlogBar" className="progress-bar"></div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

