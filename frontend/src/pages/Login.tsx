import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrandBar } from '../components/BrandBar';
import { Chip } from '../components/Chip';
import { Badge } from '../components/Badge';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { useLanguage } from '../contexts/LanguageContext';
import { api } from '../utils/apiGenerated';

export const Login: React.FC = () => {
  const { t } = useLanguage();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      showToast(t('login.enter_email'), 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      // Используем новый сгенерированный API
      const tokenResponse = await api.auth.login({
        email: trimmedEmail,
        password: trimmedPassword
      });

      // Сохраняем данные пользователя с токеном
      storage.saveUser(
        trimmedEmail,
        trimmedPassword,
        tokenResponse.access_token,
        tokenResponse.user_id,
        tokenResponse.name,
        tokenResponse.role
      );
      storage.setLogged(true);

      showToast(t('login.success'), 'success');
      setTimeout(() => navigate('/dashboard'), 500);
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error instanceof Error ? error.message : t('login.wrong_credentials');
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-shell">
      <BrandBar rightContent={<Badge variant="ghost">Prototype v1.0</Badge>} />

      <main className="auth-layout">
        <section className="auth-hero card glass">
          <div className="eyebrow">{t('login.eyebrow')}</div>
          <h1 dangerouslySetInnerHTML={{ __html: t('login.title').replace('<span>', '<span class="grad-text">') }} />
          <p className="muted">
            {t('login.desc')}
          </p>

          <div className="chips">
            <Chip>{t('login.avg_response')}</Chip>
            <Chip variant="success">{t('login.auto_resolutions')}</Chip>
            <Chip variant="warning">{t('login.sla')}</Chip>
          </div>

          <div className="mini-grid">
            <div className="mini-card">
              <p className="label">{t('login.metrics')}</p>
              <p className="stat">{t('login.metrics_desc')}</p>
            </div>
            <div className="mini-card">
              <p className="label">{t('login.entry')}</p>
              <p className="stat">{t('login.entry_desc')}</p>
            </div>
          </div>
        </section>

        <section className="auth-card card">
          <div className="auth-header">
            <div>
              <p className="eyebrow">{t('common.login')}</p>
              <h2>{t('login.welcome')}</h2>
              <p className="muted">{t('login.demo_desc')}</p>
            </div>
            <Badge variant="subtle">Demo only</Badge>
          </div>

          <div className="field">
            <label htmlFor="loginEmail">{t('common.email')}</label>
            <input
              id="loginEmail"
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            />
          </div>

          <div className="field">
            <label htmlFor="loginPassword">{t('common.password')}</label>
            <input
              id="loginPassword"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
            />
          </div>

          <button className="primary" onClick={handleLogin} disabled={isSubmitting}>
            {isSubmitting ? t('common.submitting') || 'Вход...' : t('common.login')}
          </button>

          <div className="auth-footer">
            <span className="muted">{t('common.no_account')}</span>
            <Link className="link" to="/register">
              {t('common.create')}
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

