import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead, Notification } from '../utils/notifications';
import { storage } from '../utils/storage';
import { useLanguage } from '../contexts/LanguageContext';
import { showToast } from '../utils/toast';

export const NotificationsPanel: React.FC = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const buttonRef = React.useRef<HTMLDivElement>(null);
  const [panelPosition, setPanelPosition] = useState({ top: 80, right: 20 });

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 10000); // Обновляем каждые 10 секунд
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    const user = storage.getUser();
    if (!user?.userId) return;

    try {
      setLoading(true);
      const [allNotifications, count] = await Promise.all([
        getNotifications(user.userId, true), // Только непрочитанные
        getUnreadCount(user.userId)
      ]);
      setNotifications(allNotifications);
      setUnreadCount(count);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.is_read && notification.id) {
      try {
        const user = storage.getUser();
        if (user?.userId) {
          await markAsRead(notification.id, user.userId);
          await loadNotifications();
        }
      } catch (error) {
        console.error('Error marking notification as read:', error);
      }
    }
    // Переход на тикет
    if (notification.ticket_id) {
      navigate(`/tickets/${notification.ticket_id}`);
      setIsOpen(false);
    }
  };

  const handleMarkAllAsRead = async () => {
    const user = storage.getUser();
    if (!user?.userId) return;

    try {
      await markAllAsRead(user.userId);
      await loadNotifications();
      showToast('Все уведомления помечены как прочитанные', 'success');
    } catch (error) {
      console.error('Error marking all as read:', error);
      showToast('Ошибка при обновлении уведомлений', 'error');
    }
  };

  // Вычисляем позицию панели относительно кнопки
  const updatePanelPosition = () => {
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setPanelPosition({
        top: rect.bottom + 8, // 8px отступ от кнопки
        right: window.innerWidth - rect.right // Выравнивание по правому краю кнопки
      });
    }
  };

  useEffect(() => {
    if (isOpen) {
      updatePanelPosition();
      // Обновляем позицию при изменении размера окна
      const handleResize = () => updatePanelPosition();
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, [isOpen]);

  return (
    <>
      <div ref={buttonRef} style={{ position: 'relative' }}>
        <button
          className="ghost"
          onClick={() => {
            setIsOpen(!isOpen);
            if (!isOpen) {
              // Небольшая задержка для правильного вычисления позиции
              setTimeout(updatePanelPosition, 0);
            }
          }}
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
      </div>

      {isOpen && createPortal(
        <>
          {/* Затемнение фона */}
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.4)',
              zIndex: 99998,
              cursor: 'pointer'
            }}
            onClick={() => setIsOpen(false)}
          />
          {/* Панель уведомлений */}
          <div
            style={{
              position: 'fixed',
              top: `${panelPosition.top}px`,
              right: `${panelPosition.right}px`,
              background: '#ffffff',
              border: '3px solid #007bff',
              borderRadius: '12px',
              boxShadow: '0 12px 32px rgba(0,0,0,0.4)',
              width: '420px',
              maxHeight: '600px',
              overflowY: 'auto',
              zIndex: 99999
            }}
          >
          <div style={{ 
            padding: '16px', 
            borderBottom: '2px solid #007bff', 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            background: 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)',
            borderRadius: '10px 10px 0 0'
          }}>
            <h3 style={{ margin: 0, fontSize: '1.1em', color: '#fff', fontWeight: 'bold' }}>🔔 {t('nav.notifications')}</h3>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {unreadCount > 0 && (
                <button 
                  onClick={handleMarkAllAsRead} 
                  style={{ 
                    fontSize: '0.8em', 
                    padding: '6px 12px',
                    background: '#fff',
                    color: '#007bff',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: 'bold'
                  }}
                >
                  Прочитать все
                </button>
              )}
              <button 
                onClick={() => setIsOpen(false)} 
                style={{ 
                  fontSize: '1.2em',
                  background: 'transparent',
                  border: 'none',
                  color: '#fff',
                  cursor: 'pointer',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}
              >
                ✕
              </button>
            </div>
          </div>
          
          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <div className="loader" style={{ margin: '0 auto' }}></div>
            </div>
          ) : notifications.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center' }}>
              <p style={{ color: '#666', margin: 0, fontSize: '1em' }}>✅ Нет непрочитанных уведомлений</p>
            </div>
          ) : (
            <div style={{ background: '#f8f9fa' }}>
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  style={{
                    padding: '16px',
                    borderBottom: '1px solid #e0e0e0',
                    cursor: 'pointer',
                    background: notification.is_read ? '#ffffff' : '#e3f2fd',
                    transition: 'all 0.2s',
                    borderLeft: notification.is_read ? 'none' : '5px solid #007bff',
                    position: 'relative'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = notification.is_read ? '#f5f5f5' : '#bbdefb';
                    e.currentTarget.style.transform = 'translateX(2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = notification.is_read ? '#ffffff' : '#e3f2fd';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'flex-start' }}>
                    <strong style={{ 
                      fontSize: '1em', 
                      color: notification.is_read ? '#333' : '#007bff', 
                      fontWeight: notification.is_read ? '600' : 'bold',
                      lineHeight: '1.4'
                    }}>
                      {notification.title}
                    </strong>
                    {!notification.is_read && (
                      <span style={{ 
                        width: '12px', 
                        height: '12px', 
                        background: '#007bff', 
                        borderRadius: '50%', 
                        display: 'inline-block', 
                        marginLeft: '10px', 
                        flexShrink: 0,
                        boxShadow: '0 0 4px rgba(0,123,255,0.5)'
                      }}></span>
                    )}
                  </div>
                  <p style={{ 
                    margin: '8px 0', 
                    fontSize: '0.95em', 
                    color: '#444', 
                    lineHeight: '1.6',
                    fontWeight: notification.is_read ? 'normal' : '500'
                  }}>
                    {notification.message}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                    <span style={{ fontSize: '0.85em', color: '#666', fontWeight: '500' }}>
                      📅 {format(new Date(notification.created_at), 'dd MMM HH:mm', { locale: ru })}
                    </span>
                    {!notification.is_read && (
                      <span style={{ 
                        fontSize: '0.75em', 
                        background: '#007bff', 
                        color: '#fff', 
                        padding: '2px 8px', 
                        borderRadius: '10px',
                        fontWeight: 'bold'
                      }}>
                        Новое
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          </div>
        </>,
        document.body
      )}
    </>
  );
};

