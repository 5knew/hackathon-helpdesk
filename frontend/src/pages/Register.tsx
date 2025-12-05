import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrandBar } from '../components/BrandBar';
import { Chip } from '../components/Chip';
import { Badge } from '../components/Badge';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';

export const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleRegister = () => {
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();

    if (!trimmedEmail || !trimmedPassword) {
      showToast('Введите email и пароль', 'error');
      return;
    }

    storage.saveUser(trimmedEmail, trimmedPassword);
    storage.setLogged(true);

    showToast('Регистрация успешна', 'success');
    setTimeout(() => navigate('/dashboard'), 600);
  };

  return (
    <div className="page-shell">
      <BrandBar rightContent={<Link className="link muted" to="/">Уже есть аккаунт?</Link>} />

      <main className="auth-layout">
        <section className="auth-hero card glass">
          <div className="eyebrow">Регистрация</div>
          <h1>
            Создайте доступ и подключайтесь к <span className="grad-text">панели мониторинга</span>.
          </h1>
          <p className="muted">Сохраняем логин в браузере, чтобы быстро показать прототип без сервера.</p>
          <div className="chips">
            <Chip>Демо-данные</Chip>
            <Chip variant="success">Быстрая настройка</Chip>
            <Chip variant="warning">Без бэкенда</Chip>
          </div>
        </section>

        <section className="auth-card card">
          <div className="auth-header">
            <div>
              <p className="eyebrow">Создать аккаунт</p>
              <h2>3 шага и вы в системе</h2>
              <p className="muted">Email и пароль сохраняются локально.</p>
            </div>
            <Badge variant="subtle">Demo only</Badge>
          </div>

          <div className="field">
            <label htmlFor="regEmail">Email</label>
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
            <label htmlFor="regPassword">Пароль</label>
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

          <button className="primary" onClick={handleRegister}>
            Создать аккаунт
          </button>

          <div className="auth-footer">
            <span className="muted">Уже есть доступ?</span>
            <Link className="link" to="/">
              Войти
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

