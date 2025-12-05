import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { BrandBar } from '../components/BrandBar';
import { Chip } from '../components/Chip';
import { Badge } from '../components/Badge';
import { storage } from '../utils/storage';
import { showToast } from '../utils/toast';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const user = storage.getUser();

    if (!trimmedEmail || !trimmedPassword) {
      showToast('Введите email и пароль', 'error');
      return;
    }

    if (!user || user.email !== trimmedEmail || user.password !== trimmedPassword) {
      showToast('Неверный логин или пароль', 'error');
      return;
    }

    storage.setLogged(true);
    showToast('Успешный вход!', 'success');
    setTimeout(() => navigate('/dashboard'), 500);
  };

  return (
    <div className="page-shell">
      <BrandBar rightContent={<Badge variant="ghost">Prototype v1.0</Badge>} />

      <main className="auth-layout">
        <section className="auth-hero card glass">
          <div className="eyebrow">Экспресс-поддержка</div>
          <h1>
            Единый вход для заявок, <span className="grad-text">автоматических решений</span> и мониторинга.
          </h1>
          <p className="muted">
            Отправляйте обращения, отслеживайте результат и смотрите показатели качества AI в одном месте.
          </p>

          <div className="chips">
            <Chip>0.8s среднее время ответа</Chip>
            <Chip variant="success">72% авто-решений</Chip>
            <Chip variant="warning">SLA 99.1%</Chip>
          </div>

          <div className="mini-grid">
            <div className="mini-card">
              <p className="label">Метрики</p>
              <p className="stat">В реальном времени</p>
            </div>
            <div className="mini-card">
              <p className="label">Вход</p>
              <p className="stat">Единая точка</p>
            </div>
          </div>
        </section>

        <section className="auth-card card">
          <div className="auth-header">
            <div>
              <p className="eyebrow">Войти</p>
              <h2>Добро пожаловать 👋</h2>
              <p className="muted">Используйте демо-учётку или зарегистрируйте новую.</p>
            </div>
            <Badge variant="subtle">Demo only</Badge>
          </div>

          <div className="field">
            <label htmlFor="loginEmail">Email</label>
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
            <label htmlFor="loginPassword">Пароль</label>
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

          <button className="primary" onClick={handleLogin}>
            Войти
          </button>

          <div className="auth-footer">
            <span className="muted">Нет аккаунта?</span>
            <Link className="link" to="/register">
              Создать
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
};

