import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrandBar } from '../components/BrandBar';
import { Chip } from '../components/Chip';
import { Badge } from '../components/Badge';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';
import { useLanguage } from '../contexts/LanguageContext';
import { api } from '../utils/apiGenerated';

export const Register: React.FC = () => {
  const { t } = useLanguage();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async () => {
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const trimmedName = name.trim();

    if (!trimmedEmail || !trimmedPassword || !trimmedName) {
      showToast(t('register.enter_data'), 'error');
      return;
    }

    setIsSubmitting(true);

    try {
      // Используем новый сгенерированный API для регистрации
      await api.auth.register({
        email: trimmedEmail,
        password: trimmedPassword,
        name: trimmedName,
        role: 'client' // По умолчанию
      });

      // После успешной регистрации автоматически выполняем вход для получения токена
      try {
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

        showToast(t('register.success'), 'success');
        setTimeout(() => navigate('/dashboard'), 600);
      } catch (loginError) {
        // Если вход не удался, но регистрация прошла успешно
        console.error('Auto-login after registration error:', loginError);
        showToast('Регистрация успешна, но не удалось выполнить вход. Пожалуйста, войдите вручную.', 'error');
        setTimeout(() => navigate('/'), 1000);
      }
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Ошибка при регистрации';
      showToast(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-shell">
      <BrandBar rightContent={<Link className="link muted" to="/">{t('common.has_account')}</Link>} />

      <main className="auth-layout">
        <section className="auth-hero card glass">
          <div className="eyebrow">{t('register.eyebrow')}</div>
          <h1 dangerouslySetInnerHTML={{ __html: t('register.title').replace('<span>', '<span class="grad-text">') }} />
          <p className="muted">{t('register.desc')}</p>
          <div className="chips">
            <Chip>{t('register.demo')}</Chip>
            <Chip variant="success">{t('register.quick_setup')}</Chip>
            <Chip variant="success">API Connected</Chip>
          </div>
        </section>

        <section className="auth-card card">
          <div className="auth-header">
            <div>
              <p className="eyebrow">{t('common.create_account')}</p>
              <h2>{t('register.steps')}</h2>
              <p className="muted">{t('register.local_desc')}</p>
            </div>
            <Badge variant="subtle">API Ready</Badge>
          </div>

          <div className="field">
            <label htmlFor="regName">{t('common.name') || 'Имя'}</label>
            <input
              id="regName"
              type="text"
              placeholder="Иван Иванов"
              autoComplete="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleRegister()}
            />
          </div>

          <div className="field">
            <label htmlFor="regEmail">{t('common.email')}</label>
            <input
              id="regEmail"
              type="email"
              placeholder="you@example.com"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleRegister()}
            />
          </div>

          <div className="field">
            <label htmlFor="regPassword">{t('common.password')}</label>
            <input
              id="regPassword"
              type="password"
              placeholder="••••••••"
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleRegister()}
            />
          </div>

          <button className="primary" onClick={handleRegister} disabled={isSubmitting}>
            {isSubmitting ? t('common.submitting') || 'Регистрация...' : t('common.create_account')}
          </button>

          <div className="auth-footer">
            <span className="muted">{t('common.has_account')}</span>
            <Link className="link" to="/">
              {t('common.login')}
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

