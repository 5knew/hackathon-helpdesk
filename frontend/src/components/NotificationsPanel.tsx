import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { getAllNotifications, markNotificationAsRead, getUnreadNotificationsCount } from '../utils/notifications';
import { useLanguage } from '../contexts/LanguageContext';
import { showToast } from '../utils/toast';

interface Notification {
  id: number;
  ticket_id: number;
  ticket_subject: string;
  type: 'created' | 'updated' | 'closed' | 'comment';
  email: string;
  timestamp: string;
  read: boolean;
  message: string;
}

export const NotificationsPanel: React.FC = () => {
  const { t } = useLanguage();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 5000); // Обновляем каждые 5 секунд
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = () => {
    const all = getAllNotifications();
    setNotifications(all);
    setUnreadCount(getUnreadNotificationsCount());
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markNotificationAsRead(notification.id);
      loadNotifications();
    }
    // Переход на тикет
    window.location.href = `/tickets/${notification.ticket_id}`;
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        className="ghost"
        onClick={() => setIsOpen(!isOpen)}
        style={{ position: 'relative', padding: '8px 12px' }}
      >
        📧 {t('nav.notifications')}
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              background: '#dc3545',
              color: 'white',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.7em',
              fontWeight: 'bold'
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: '8px',
            background: 'white',
            border: '1px solid #ddd',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            width: '400px',
            maxHeight: '500px',
            overflowY: 'auto',
            zIndex: 1000
          }}
        >
          <div style={{ padding: '12px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, fontSize: '1em' }}>{t('nav.notifications')}</h3>
            <button className="ghost" onClick={() => setIsOpen(false)} style={{ fontSize: '0.85em' }}>
              ✕
            </button>
          </div>
          
          {notifications.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center' }}>
              <p className="muted">{t('notifications.empty')}</p>
            </div>
          ) : (
            <div>
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  style={{
                    padding: '12px',
                    borderBottom: '1px solid #eee',
                    cursor: 'pointer',
                    background: notification.read ? 'white' : '#f0f8ff',
                    transition: 'background 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#f8f9fa'}
                  onMouseLeave={(e) => e.currentTarget.style.background = notification.read ? 'white' : '#f0f8ff'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <strong style={{ fontSize: '0.9em' }}>{notification.ticket_subject}</strong>
                    {!notification.read && (
                      <span style={{ width: '8px', height: '8px', background: '#007bff', borderRadius: '50%', display: 'inline-block' }}></span>
                    )}
                  </div>
                  <p style={{ margin: '4px 0', fontSize: '0.85em', color: '#666' }}>{notification.message}</p>
                  <span style={{ fontSize: '0.75em', color: '#999' }}>
                    {format(new Date(notification.timestamp), 'dd MMM HH:mm', { locale: ru })}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

