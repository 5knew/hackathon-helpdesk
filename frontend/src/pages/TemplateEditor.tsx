import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Template } from '../types';
import { getTemplates } from '../utils/ticket';
import { apiRequest } from '../utils/apiConfig';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { useLanguage } from '../contexts/LanguageContext';

export const TemplateEditor: React.FC = () => {
  const { t } = useLanguage();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [newTemplate, setNewTemplate] = useState({ name: '', category: '', text: '', language: 'ru' as 'ru' | 'kz' | 'en' });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!storage.isLogged()) {
      navigate('/');
      return;
    }
    loadTemplates();
  }, [navigate]);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data = await getTemplates();
      setTemplates(data);
    } catch (error) {
      showToast(t('settings.load_error'), 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveTemplate = async () => {
    if (!newTemplate.name || !newTemplate.text) {
      showToast(t('settings.template_required'), 'error');
      return;
    }
    
    try {
      if (editingTemplate) {
        // Обновляем существующий шаблон
        await apiRequest(`/templates/${editingTemplate.id}`, {
          method: 'PUT',
          body: JSON.stringify({
            name: newTemplate.name,
            content: newTemplate.text,
            category_id: newTemplate.category || null
          })
        });
        showToast(t('settings.template_updated'), 'success');
      } else {
        // Создаем новый шаблон
        await apiRequest('/templates', {
          method: 'POST',
          body: JSON.stringify({
            name: newTemplate.name,
            content: newTemplate.text,
            category_id: newTemplate.category || null
          })
        });
        showToast(t('settings.template_created'), 'success');
      }
      
      setEditingTemplate(null);
      setNewTemplate({ name: '', category: '', text: '', language: 'ru' });
      await loadTemplates(); // Перезагружаем список
    } catch (error) {
      console.error('Error saving template:', error);
      showToast(t('settings.template_save_error') || 'Ошибка сохранения шаблона', 'error');
    }
  };

  const handleDeleteTemplate = async (id: number | string) => {
    if (!window.confirm(t('settings.template_delete_confirm'))) {
      return;
    }
    
    try {
      await apiRequest(`/templates/${id}`, {
        method: 'DELETE'
      });
      showToast(t('settings.template_deleted'), 'success');
      await loadTemplates(); // Перезагружаем список
    } catch (error) {
      console.error('Error deleting template:', error);
      showToast(t('settings.template_delete_error') || 'Ошибка удаления шаблона', 'error');
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
            <p className="brand-name">{t('app.name')}</p>
            <span className="brand-sub">{t('settings.templates_editor')}</span>
          </div>
        </div>
        <div className="topbar-actions">
          <Link to="/settings" className="ghost" style={{ marginRight: '12px' }}>
            {t('common.back')}
          </Link>
          <button className="ghost" onClick={() => { storage.setLogged(false); navigate('/'); }}>
            {t('common.logout')}
          </button>
        </div>
      </header>

      <main style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        <div className="card" style={{ marginBottom: '24px' }}>
          <h2 style={{ margin: '0 0 16px 0' }}>{t('settings.templates_editor')}</h2>
          <p className="muted" style={{ marginBottom: '16px' }}>
            {t('settings.templates_editor_desc')}
          </p>

          {/* Форма создания/редактирования */}
          <div style={{ padding: '16px', background: '#f8f9fa', borderRadius: '8px', marginBottom: '16px' }}>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1em' }}>
              {editingTemplate ? t('settings.edit_template') : t('settings.create_template')}
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
              <div className="field">
                <label>{t('settings.template_name')}</label>
                <input
                  type="text"
                  value={newTemplate.name}
                  onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                  placeholder={t('settings.template_name_placeholder')}
                />
              </div>
              <div className="field">
                <label>{t('settings.template_category')}</label>
                <input
                  type="text"
                  value={newTemplate.category}
                  onChange={(e) => setNewTemplate({ ...newTemplate, category: e.target.value })}
                  placeholder={t('settings.template_category_placeholder')}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '12px', marginBottom: '12px' }}>
              <div className="field">
                <label>{t('settings.template_language')}</label>
                <select
                  value={newTemplate.language}
                  onChange={(e) => setNewTemplate({ ...newTemplate, language: e.target.value as 'ru' | 'kz' | 'en' })}
                >
                  <option value="ru">Русский</option>
                  <option value="kz">Қазақша</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>

            <div className="field" style={{ marginBottom: '12px' }}>
              <label>{t('settings.template_text')}</label>
              <textarea
                rows={4}
                value={newTemplate.text}
                onChange={(e) => setNewTemplate({ ...newTemplate, text: e.target.value })}
                placeholder={t('settings.template_text_placeholder')}
              />
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button className="primary" onClick={handleSaveTemplate}>
                {editingTemplate ? t('common.save') : t('settings.create_template')}
              </button>
              {editingTemplate && (
                <button className="ghost" onClick={() => {
                  setEditingTemplate(null);
                  setNewTemplate({ name: '', category: '', text: '', language: 'ru' });
                }}>
                  {t('common.cancel')}
                </button>
              )}
            </div>
          </div>

          {/* Список шаблонов */}
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1em' }}>{t('settings.existing_templates')}</h3>
            {templates.length === 0 ? (
              <p className="muted" style={{ textAlign: 'center', padding: '24px' }}>
                {t('settings.templates_not_found')}
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {templates.map((template) => (
                  <div
                    key={template.id}
                    style={{
                      padding: '16px',
                      background: '#f8f9fa',
                      borderRadius: '8px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '8px' }}>
                        <h4 style={{ margin: 0, fontSize: '1em' }}>{template.name}</h4>
                        <span className="chip ghost" style={{ fontSize: '0.75em' }}>
                          {template.category}
                        </span>
                        <span className="chip ghost" style={{ fontSize: '0.75em' }}>
                          {template.language === 'ru' ? 'Русский' : template.language === 'kz' ? 'Қазақша' : 'English'}
                        </span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.9em', whiteSpace: 'pre-wrap' }}>{template.text}</p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
                      <button
                        className="secondary"
                        style={{ fontSize: '0.85em', padding: '6px 12px' }}
                        onClick={() => {
                          setEditingTemplate(template);
                          setNewTemplate({
                            name: template.name,
                            category: template.category,
                            text: template.text,
                            language: template.language
                          });
                        }}
                      >
                        {t('common.edit')}
                      </button>
                      <button
                        className="ghost"
                        style={{ fontSize: '0.85em', padding: '6px 12px', color: '#dc3545' }}
                        onClick={() => handleDeleteTemplate(template.id)}
                      >
                        {t('common.delete')}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

