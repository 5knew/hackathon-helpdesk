import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Ticket, Comment, TicketHistory } from '../types';
import { getTicketById, getTicketComments, addComment, getTicketHistory, submitCSAT, getTemplates } from '../utils/api';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Template } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { simulateEmailNotification } from '../utils/notifications';

export const TicketDetail: React.FC = () => {
  const { t } = useLanguage();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [history, setHistory] = useState<TicketHistory[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submittingComment, setSubmittingComment] = useState(false);
  const [showCSAT, setShowCSAT] = useState(false);
  const [csatScore, setCsatScore] = useState(0);
  const [csatComment, setCsatComment] = useState('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showTemplates, setShowTemplates] = useState(false);

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }
    if (id) {
      loadTicketData();
    }
  }, [id, navigate]);

  const loadTicketData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [ticketData, commentsData, historyData] = await Promise.all([
        getTicketById(Number(id)),
        getTicketComments(Number(id)),
        getTicketHistory(Number(id))
      ]);
      setTicket(ticketData);
      setComments(commentsData);
      setHistory(historyData);
      
      // Загружаем шаблоны после получения тикета
      if (ticketData) {
        const templatesData = await getTemplates(ticketData.category);
        setTemplates(templatesData);
      }
      
      // Показываем CSAT модалку если тикет закрыт и нет оценки
      if (ticketData && ticketData.status === 'Closed' && !ticketData.csat_score) {
        setShowCSAT(true);
      }
    } catch (error) {
      showToast(t('error.load_data'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim() || !id) return;
    setSubmittingComment(true);
    try {
      const comment = await addComment(Number(id), newComment);
      setComments([...comments, comment]);
      setNewComment('');
      showToast(t('error.comment_added'), 'success');
      
      // Имитация email-уведомления
      if (ticket) {
        simulateEmailNotification(ticket, 'comment');
      }
    } catch (error) {
      showToast(t('error.add_comment'), 'error');
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleSubmitCSAT = async () => {
    if (!id || csatScore === 0) {
      showToast(t('tickets.detail.csat.select_rating'), 'error');
      return;
    }
    try {
      await submitCSAT(Number(id), csatScore, csatComment);
      showToast(t('tickets.detail.csat.thanks'), 'success');
      setShowCSAT(false);
      loadTicketData();
    } catch (error) {
      showToast(t('tickets.detail.csat.error'), 'error');
    }
  };

  if (loading) {
    return (
      <div className="page-shell">
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <div className="loader"></div>
          <p className="muted">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div className="page-shell">
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
            <p className="muted">{t('tickets.detail.not_found')}</p>
            <Link to="/tickets" className="primary" style={{ marginTop: '16px', display: 'inline-block' }}>
              {t('tickets.detail.return')}
            </Link>
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
            <span className="brand-sub">{t('tickets.detail.title')} #{ticket.id}</span>
          </div>
        </div>
        <div className="topbar-actions">
          <Link to="/tickets" className="ghost" style={{ marginRight: '12px' }}>
            {t('tickets.back_to_tickets')}
          </Link>
          <button className="ghost" onClick={() => { storage.setLogged(false); navigate('/'); }}>
            {t('common.logout')}
          </button>
        </div>
      </header>

      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Информация о тикете */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
            <div>
              <h1 style={{ margin: '0 0 8px 0' }}>{ticket.subject}</h1>
              <p className="muted">{t('tickets.detail.created')}: {format(new Date(ticket.created_at), 'dd MMMM yyyy, HH:mm', { locale: ru })}</p>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              <span className={`chip ${ticket.status === 'Closed' ? 'success' : ticket.status === 'In Progress' ? 'info' : 'ghost'}`}>
                {ticket.status === 'Open' ? t('tickets.status.open') : 
                 ticket.status === 'In Progress' ? t('tickets.status.in_progress') :
                 ticket.status === 'Closed' ? t('tickets.status.closed') : t('tickets.status.waiting')}
              </span>
              <span className="chip ghost">{ticket.category}</span>
              <span className={`chip ${ticket.priority === 'Высокий' ? 'error' : ticket.priority === 'Средний' ? 'warning' : 'ghost'}`}>
                {ticket.priority}
              </span>
              {ticket.auto_closed && <span className="chip success">{t('tickets.auto_closed')}</span>}
            </div>
          </div>

          <div style={{ padding: '16px', background: '#f8f9fa', borderRadius: '8px', marginBottom: '16px' }}>
            <h3 style={{ margin: '0 0 8px 0', fontSize: '1em' }}>{t('tickets.detail.description')}</h3>
            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{ticket.problem_description}</p>
          </div>

          {ticket.sla_deadline && (() => {
            const deadline = new Date(ticket.sla_deadline);
            const now = new Date();
            const hoursLeft = Math.floor((deadline.getTime() - now.getTime()) / 3600000);
            const isUrgent = hoursLeft < 24 && hoursLeft > 0;
            const isOverdue = hoursLeft < 0;
            const isEscalated = hoursLeft < 12 && hoursLeft > 0;
            
            return (
              <div style={{ 
                padding: '12px', 
                background: isOverdue ? '#f8d7da' : isUrgent ? '#fff3cd' : '#d1ecf1',
                borderRadius: '6px', 
                marginBottom: '16px',
                borderLeft: isOverdue ? '4px solid #dc3545' : isUrgent ? '4px solid #ffc107' : '4px solid #17a2b8'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{t('tickets.sla_deadline')}:</strong> {format(deadline, 'dd MMMM yyyy, HH:mm', { locale: ru })}
                    {isOverdue && (
                      <span style={{ marginLeft: '8px', color: '#dc3545', fontWeight: 'bold' }}>
                        ⚠️ {t('tickets.sla_overdue')}
                      </span>
                    )}
                    {isUrgent && !isOverdue && (
                      <span style={{ marginLeft: '8px', color: '#ff9800', fontWeight: 'bold' }}>
                        ⏰ {t('tickets.sla_urgent')} ({hoursLeft}ч)
                      </span>
                    )}
                    {isEscalated && (
                      <div style={{ marginTop: '8px', padding: '8px', background: '#fff', borderRadius: '4px' }}>
                        <strong style={{ color: '#dc3545' }}>🚨 {t('tickets.auto_escalated')}</strong>
                        <p style={{ margin: '4px 0 0 0', fontSize: '0.85em' }}>
                          {t('tickets.escalation_message')}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })()}

          {ticket.csat_score && (
            <div style={{ padding: '12px', background: '#d4edda', borderRadius: '6px' }}>
              <strong>{t('tickets.detail.satisfaction')}:</strong> {ticket.csat_score}/5 ⭐
              {ticket.csat_comment && <p style={{ margin: '8px 0 0 0' }}>{ticket.csat_comment}</p>}
            </div>
          )}
        </div>

        {/* Переписка */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0' }}>{t('tickets.detail.comments')}</h2>
          
          <div style={{ maxHeight: '500px', overflowY: 'auto', marginBottom: '16px' }}>
            {comments.length === 0 ? (
              <p className="muted" style={{ textAlign: 'center', padding: '24px' }}>{t('tickets.detail.no_comments')}</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {comments.map((comment, index) => {
                  // Вычисляем время ответа относительно предыдущего комментария или создания тикета
                  const commentTime = new Date(comment.created_at);
                  const prevCommentTime = index > 0 ? new Date(comments[index - 1].created_at) : ticket ? new Date(ticket.created_at) : commentTime;
                  const responseTimeMinutes = Math.floor((commentTime.getTime() - prevCommentTime.getTime()) / 60000);
                  
                  return (
                  <div
                    key={comment.id}
                    style={{
                      padding: '16px',
                      background: comment.author_type === 'system' ? '#e7f3ff' : 
                                  comment.is_auto_reply ? '#fff3cd' : 
                                  comment.author_type === 'operator' ? '#e8f5e9' : '#f8f9fa',
                      borderRadius: '8px',
                      borderLeft: comment.author_type === 'user' ? '4px solid #007bff' : 
                                 comment.is_auto_reply ? '4px solid #ffc107' : 
                                 comment.author_type === 'operator' ? '4px solid #28a745' : '4px solid #17a2b8',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                        <strong style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {comment.author_type === 'user' && '👤'}
                          {comment.author_type === 'operator' && '👨‍💼'}
                          {comment.author_type === 'system' && '🤖'}
                          {comment.author}
                        </strong>
                        {comment.is_auto_reply && (
                          <span className="chip success" style={{ fontSize: '0.75em', padding: '2px 8px' }}>
                            🤖 {t('tickets.detail.auto_reply')}
                          </span>
                        )}
                        {comment.author_type === 'system' && !comment.is_auto_reply && (
                          <span className="chip info" style={{ fontSize: '0.75em', padding: '2px 8px' }}>
                            {t('tickets.detail.system')}
                          </span>
                        )}
                        {comment.author_type === 'operator' && (
                          <span className="chip" style={{ fontSize: '0.75em', padding: '2px 8px', background: '#e7f3ff', color: '#0066cc' }}>
                            {t('tickets.detail.operator')}
                          </span>
                        )}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                        <span className="muted" style={{ fontSize: '0.85em' }}>
                          {format(new Date(comment.created_at), 'dd MMM HH:mm', { locale: ru })}
                        </span>
                      </div>
                    </div>
                    <p style={{ margin: '0 0 8px 0', whiteSpace: 'pre-wrap', lineHeight: '1.5' }}>{comment.text}</p>
                    {responseTimeMinutes > 0 && responseTimeMinutes < 1440 && (
                      <div style={{ fontSize: '0.75em', color: '#666', fontStyle: 'italic', marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #ddd' }}>
                        ⏱️ {t('tickets.detail.response_time')}: {responseTimeMinutes < 60 
                          ? `${responseTimeMinutes} ${t('tickets.detail.minutes')}`
                          : `${Math.floor(responseTimeMinutes / 60)} ${t('tickets.detail.hours')}`}
                      </div>
                    )}
                  </div>
                  );
                })}
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <button
              className="secondary"
              onClick={() => setShowTemplates(!showTemplates)}
            >
              {showTemplates ? t('tickets.detail.templates_hide') : t('tickets.detail.templates')}
            </button>
          </div>

          {showTemplates && templates.length > 0 && (
            <div style={{ marginBottom: '12px', padding: '12px', background: '#f8f9fa', borderRadius: '6px' }}>
              <p style={{ margin: '0 0 8px 0', fontSize: '0.9em', fontWeight: 'bold' }}>{t('tickets.detail.templates_title')}</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {templates.map((template) => (
                  <button
                    key={template.id}
                    className="ghost"
                    style={{ textAlign: 'left', padding: '8px', fontSize: '0.85em' }}
                    onClick={() => {
                      setNewComment(template.text);
                      setShowTemplates(false);
                    }}
                  >
                    <strong>{template.name}</strong> - {template.text.substring(0, 50)}...
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="field">
            <textarea
              placeholder={t('tickets.detail.add_comment')}
              rows={3}
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
            />
          </div>
          <button
            className="primary"
            onClick={handleAddComment}
            disabled={!newComment.trim() || submittingComment}
          >
            {submittingComment ? t('tickets.detail.sending') : t('tickets.detail.send_comment')}
          </button>
        </div>

        {/* История изменений */}
        {history.length > 0 && (
          <div className="card">
            <h2 style={{ margin: '0 0 16px 0' }}>{t('tickets.detail.history')}</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((item) => (
                <div
                  key={item.id}
                  style={{
                    padding: '12px',
                    background: '#f8f9fa',
                    borderRadius: '6px',
                    borderLeft: '3px solid #007bff'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <strong>{item.action}</strong>
                    <span className="muted" style={{ fontSize: '0.85em' }}>
                      {format(new Date(item.created_at), 'dd MMM HH:mm', { locale: ru })}
                    </span>
                  </div>
                  <p className="muted" style={{ fontSize: '0.85em', margin: '4px 0 0 0' }}>
                    {t('tickets.detail.changed_by')}: {item.changed_by}
                    {item.old_value && item.new_value && (
                      <span> • {item.old_value} → {item.new_value}</span>
                    )}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* CSAT Модалка */}
      {showCSAT && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000
          }}
          onClick={() => setShowCSAT(false)}
        >
          <div
            className="card"
            style={{ maxWidth: '500px', width: '90%', zIndex: 1001 }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ margin: '0 0 16px 0' }}>{t('tickets.detail.csat.title')}</h2>
            <p className="muted" style={{ marginBottom: '16px' }}>
              {t('tickets.detail.csat.desc')}
            </p>
            
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '16px' }}>
              {[1, 2, 3, 4, 5].map((score) => (
                <button
                  key={score}
                  className={csatScore === score ? 'primary' : 'ghost'}
                  onClick={() => setCsatScore(score)}
                  style={{
                    fontSize: '2em',
                    width: '60px',
                    height: '60px',
                    padding: 0,
                    borderRadius: '50%'
                  }}
                >
                  ⭐
                </button>
              ))}
            </div>

            <div className="field">
              <label>{t('tickets.detail.csat.comment')}</label>
              <textarea
                rows={3}
                value={csatComment}
                onChange={(e) => setCsatComment(e.target.value)}
                placeholder={t('tickets.detail.csat.comment_placeholder')}
              />
            </div>

            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button className="ghost" onClick={() => setShowCSAT(false)}>
                {t('tickets.detail.csat.skip')}
              </button>
              <button className="primary" onClick={handleSubmitCSAT} disabled={csatScore === 0}>
                {t('tickets.detail.csat.submit')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

