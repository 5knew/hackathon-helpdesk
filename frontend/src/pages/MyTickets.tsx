import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Ticket, TicketFilter } from '../types';
import { getTickets, searchTickets } from '../utils/ticket';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useLanguage } from '../contexts/LanguageContext';

export const MyTickets: React.FC = () => {
  const { t } = useLanguage();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<TicketFilter>({});
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [savedSearches, setSavedSearches] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }
    loadTickets();
    loadSavedSearches();
  }, [navigate, filter]);

  useEffect(() => {
    // Автодополнение при вводе
    if (searchQuery.length > 2) {
      const saved = localStorage.getItem('ticket_search_history');
      const history = saved ? JSON.parse(saved) : [];
      const filtered = history.filter((s: string) => 
        s.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery]);

  const loadSavedSearches = () => {
    const saved = localStorage.getItem('saved_searches');
    if (saved) {
      setSavedSearches(JSON.parse(saved));
    }
  };

  const saveSearch = () => {
    if (searchQuery.trim()) {
      const newSearches = [...savedSearches, searchQuery.trim()].slice(-10);
      setSavedSearches(newSearches);
      localStorage.setItem('saved_searches', JSON.stringify(newSearches));
      
      // Сохраняем в историю поиска
      const history = JSON.parse(localStorage.getItem('ticket_search_history') || '[]');
      if (!history.includes(searchQuery.trim())) {
        history.unshift(searchQuery.trim());
        localStorage.setItem('ticket_search_history', JSON.stringify(history.slice(0, 20)));
      }
    }
  };

  const loadTickets = async () => {
    setLoading(true);
    try {
      const user = storage.getUser();
      if (searchQuery.trim()) {
        // Используем поиск
        const searchResult = await searchTickets(searchQuery) as { tickets: Ticket[]; total: number; query: string };
        setTickets(searchResult.tickets);
      } else {
        // Используем обычный список с фильтрами
        const response = await getTickets(
          user?.email,
          filter.status?.[0],
          filter.category?.[0],
          undefined,
          50,
          0
        );
        setTickets(response.tickets);
      }
    } catch (error) {
      showToast(t('error.load_tickets') || 'Ошибка при загрузке заявок', 'error');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    saveSearch();
    loadTickets();
    setShowSuggestions(false);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    setShowSuggestions(false);
    loadTickets();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Closed': return 'success';
      case 'In Progress': return 'info';
      case 'Waiting': return 'warning';
      default: return 'ghost';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Высокий': return 'error';
      case 'Средний': return 'warning';
      default: return 'ghost';
    }
  };

  return (
    <div className="page-shell">
      <header className="topbar card glass">
        <div className="brand">
          <div className="logo-dot"></div>
          <div>
            <p className="brand-name">{t('app.name')}</p>
            <span className="brand-sub">{t('tickets.subtitle')}</span>
          </div>
        </div>
        <div className="topbar-actions">
          <Link to="/dashboard" className="ghost" style={{ marginRight: '12px' }}>
            {t('nav.dashboard')}
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
              <h2>{t('tickets.history')}</h2>
              <p className="muted">{t('tickets.all')}</p>
            </div>
            <Link to="/dashboard" className="primary">
              {t('tickets.new')}
            </Link>
          </div>

          {/* Поиск с автодополнением */}
          <form onSubmit={handleSearch} style={{ marginBottom: '16px', position: 'relative' }}>
            <div className="field" style={{ display: 'flex', gap: '8px', position: 'relative' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <input
                  type="text"
                  placeholder={t('tickets.search')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => searchQuery.length > 2 && setShowSuggestions(true)}
                  style={{ width: '100%' }}
                />
                {showSuggestions && suggestions.length > 0 && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    background: 'white',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    marginTop: '4px',
                    zIndex: 100,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    maxHeight: '200px',
                    overflowY: 'auto'
                  }}>
                    {suggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        style={{
                          padding: '8px 12px',
                          cursor: 'pointer',
                          borderBottom: idx < suggestions.length - 1 ? '1px solid #eee' : 'none'
                        }}
                        onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
                        onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                      >
                        {suggestion}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <button type="submit" className="secondary">{t('tickets.find')}</button>
            </div>
            
            {/* Сохраненные поисковые запросы */}
            {savedSearches.length > 0 && (
              <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                <span className="muted" style={{ fontSize: '0.85em' }}>{t('tickets.saved_searches')}:</span>
                {savedSearches.slice(0, 5).map((search, idx) => (
                  <button
                    key={idx}
                    className="ghost"
                    style={{ fontSize: '0.85em', padding: '4px 8px' }}
                    onClick={() => {
                      setSearchQuery(search);
                      loadTickets();
                    }}
                  >
                    {search}
                  </button>
                ))}
                {savedSearches.length > 5 && (
                  <span className="muted" style={{ fontSize: '0.85em' }}>+{savedSearches.length - 5}</span>
                )}
              </div>
            )}
          </form>

          {/* Фильтры */}
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '16px' }}>
            <select
              value={filter.status?.[0] || ''}
              onChange={(e) => setFilter({ ...filter, status: e.target.value ? [e.target.value] : undefined })}
              style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd' }}
            >
              <option value="">{t('tickets.all_statuses')}</option>
              <option value="Open">{t('tickets.status.open')}</option>
              <option value="In Progress">{t('tickets.status.in_progress')}</option>
              <option value="Closed">{t('tickets.status.closed')}</option>
              <option value="Waiting">{t('tickets.status.waiting')}</option>
            </select>

            <select
              value={filter.category?.[0] || ''}
              onChange={(e) => setFilter({ ...filter, category: e.target.value ? [e.target.value] : undefined })}
              style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd' }}
            >
              <option value="">{t('tickets.all_categories')}</option>
              <option value="Техническая поддержка">Техническая поддержка</option>
              <option value="IT поддержка">IT поддержка</option>
              <option value="Биллинг и платежи">Биллинг и платежи</option>
              <option value="HR">HR</option>
            </select>

            <input
              type="date"
              value={filter.dateFrom || ''}
              onChange={(e) => setFilter({ ...filter, dateFrom: e.target.value || undefined })}
              placeholder={t('tickets.from_date')}
              style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd' }}
            />

            <input
              type="date"
              value={filter.dateTo || ''}
              onChange={(e) => setFilter({ ...filter, dateTo: e.target.value || undefined })}
              placeholder={t('tickets.to_date')}
              style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #ddd' }}
            />

            {(filter.status || filter.category || filter.dateFrom || filter.dateTo) && (
              <button
                className="ghost"
                onClick={() => setFilter({})}
              >
                {t('tickets.reset')}
              </button>
            )}
          </div>
        </div>

        {/* Список тикетов */}
        {loading ? (
          <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
            <div className="loader"></div>
            <p className="muted">Загрузка заявок...</p>
          </div>
        ) : tickets.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
            <p className="muted">{t('tickets.not_found')}</p>
            <Link to="/dashboard" className="primary" style={{ marginTop: '16px', display: 'inline-block' }}>
              {t('tickets.create')}
            </Link>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {tickets.map((ticket) => (
              <Link
                key={ticket.id}
                to={`/tickets/${ticket.id}`}
                className="card"
                style={{
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'block',
                  transition: 'transform 0.2s, box-shadow 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '';
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 8px 0', fontSize: '1.1em' }}>{ticket.subject}</h3>
                    <p className="muted" style={{ margin: '0 0 8px 0', fontSize: '0.9em' }}>
                      {ticket.problem_description.substring(0, 150)}
                      {ticket.problem_description.length > 150 && '...'}
                    </p>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                      <span className={`chip ${getStatusColor(ticket.status)}`}>
                        {ticket.status === 'Open' ? t('tickets.status.open') : 
                         ticket.status === 'In Progress' ? t('tickets.status.in_progress') :
                         ticket.status === 'Closed' ? t('tickets.status.closed') : t('tickets.status.waiting')}
                      </span>
                      <span className="chip ghost">{ticket.category}</span>
                      <span className={`chip ${getPriorityColor(ticket.priority)}`}>
                        {ticket.priority}
                      </span>
                      {ticket.queue === 'Automated' && (
                        <span className="chip success">{t('tickets.auto_closed') || 'Автоматически закрыто'}</span>
                      )}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', minWidth: '120px' }}>
                    {ticket.created_at && (
                      <>
                        <p className="muted" style={{ fontSize: '0.85em', margin: '0 0 4px 0' }}>
                          {format(new Date(ticket.created_at), 'dd MMM yyyy', { locale: ru })}
                        </p>
                        <p className="muted" style={{ fontSize: '0.85em' }}>
                          {format(new Date(ticket.created_at), 'HH:mm')}
                        </p>
                      </>
                    )}
                    {ticket.sla_deadline && (() => {
            const deadline = new Date(ticket.sla_deadline);
            const now = new Date();
            const hoursLeft = Math.floor((deadline.getTime() - now.getTime()) / 3600000);
            const isUrgent = hoursLeft < 24 && hoursLeft > 0;
            const isOverdue = hoursLeft < 0;
            
            return (
              <p style={{ 
                fontSize: '0.75em', 
                color: isOverdue ? '#dc3545' : isUrgent ? '#ff9800' : '#666',
                marginTop: '4px',
                fontWeight: isUrgent || isOverdue ? 'bold' : 'normal'
              }}>
                {isOverdue ? '⚠️ ' : isUrgent ? '⏰ ' : ''}
                SLA: {format(deadline, 'dd.MM HH:mm')}
                {isUrgent && ` (${hoursLeft}ч осталось)`}
                {isOverdue && ` (Просрочено!)`}
              </p>
            );
          })()}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

