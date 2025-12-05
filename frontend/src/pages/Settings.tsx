import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Integration, Template, Language } from '../types';
import { getIntegrations, getTemplates } from '../utils/api';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { useLanguage } from '../contexts/LanguageContext';

export const Settings: React.FC = () => {
  const { language: currentLang, setLanguage, t } = useLanguage();
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }
    loadData();
  }, [navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [integrationsData, templatesData] = await Promise.all([
        getIntegrations(),
        getTemplates()
      ]);
      setIntegrations(integrationsData);
      setTemplates(templatesData);
    } catch (error) {
      showToast(t('settings.load_error'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    showToast(t('settings.language_changed'), 'success');
  };

  const handleIntegrationToggle = async (id: string, enabled: boolean) => {
    try {
      // Здесь будет API вызов для обновления интеграции
      setIntegrations(integrations.map(int => 
        int.id === id ? { ...int, enabled } : int
      ));
      showToast(t('settings.saved'), 'success');
    } catch (error) {
      showToast(t('settings.save_error'), 'error');
    }
  };

  if (loading) {
    return (
      <div className="page-shell">
        <div className="card" style={{ textAlign: 'center', padding: '48px' }}>
          <div className="loader"></div>
          <p className="muted">{t('settings.loading')}</p>
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
            <p className="brand-name">AI AutoResponder</p>
            <span className="brand-sub">{t('settings.subtitle')}</span>
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

      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Язык */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0' }}>{t('settings.language')}</h2>
          <p className="muted" style={{ marginBottom: '16px' }}>
            {t('settings.language_desc')}
          </p>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <button
              className={currentLang === 'ru' ? 'primary' : 'secondary'}
              onClick={() => handleLanguageChange('ru')}
            >
              Русский
            </button>
            <button
              className={currentLang === 'kz' ? 'primary' : 'secondary'}
              onClick={() => handleLanguageChange('kz')}
            >
              Қазақша
            </button>
            <button
              className={currentLang === 'en' ? 'primary' : 'secondary'}
              onClick={() => handleLanguageChange('en')}
            >
              English
            </button>
          </div>
        </div>

        {/* Интеграции */}
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0' }}>{t('settings.integrations')}</h2>
          <p className="muted" style={{ marginBottom: '16px' }}>
            {t('settings.integrations_desc')}
          </p>
          
          {integrations.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', background: '#f8f9fa', borderRadius: '8px' }}>
              <p className="muted">{t('settings.integrations_not_configured')}</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {integrations.map((integration) => (
                <div
                  key={integration.id}
                  style={{
                    padding: '16px',
                    background: '#f8f9fa',
                    borderRadius: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <div>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '1em' }}>{integration.name}</h3>
                    <p className="muted" style={{ margin: 0, fontSize: '0.85em' }}>
                      {t('settings.type')}: {integration.type}
                      {integration.last_sync && ` • ${t('settings.last_sync')}: ${new Date(integration.last_sync).toLocaleString('ru')}`}
                    </p>
                  </div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      checked={integration.enabled}
                      onChange={(e) => handleIntegrationToggle(integration.id, e.target.checked)}
                    />
                    <span>{integration.enabled ? t('settings.enabled') : t('settings.disabled')}</span>
                  </label>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Шаблоны ответов */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h2 style={{ margin: '0 0 8px 0' }}>{t('settings.templates')}</h2>
              <p className="muted" style={{ margin: 0 }}>
                {t('settings.templates_desc')}
              </p>
            </div>
            <Link to="/settings/templates" className="primary">
              {t('settings.templates_editor')}
            </Link>
          </div>
          
          {templates.length === 0 ? (
            <div style={{ padding: '24px', textAlign: 'center', background: '#f8f9fa', borderRadius: '8px' }}>
              <p className="muted">{t('settings.templates_not_found')}</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {templates.map((template) => (
                <div
                  key={template.id}
                  style={{
                    padding: '16px',
                    background: '#f8f9fa',
                    borderRadius: '8px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div>
                      <h3 style={{ margin: '0 0 4px 0', fontSize: '1em' }}>{template.name}</h3>
                      <span className="chip ghost" style={{ fontSize: '0.75em' }}>
                        {template.category} • {template.language === 'ru' ? 'Русский' : template.language === 'kz' ? 'Қазақша' : 'English'}
                      </span>
                    </div>
                  </div>
                  <p style={{ margin: '8px 0 0 0', whiteSpace: 'pre-wrap', fontSize: '0.9em' }}>{template.text}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

