import { User } from '../types';

interface StoredUser extends User {
  token?: string;
  userId?: string;
  name?: string;
  role?: string;
}

export const storage = {
  saveUser(email: string, password: string, token?: string, userId?: string, name?: string, role?: string): void {
    const user: StoredUser = { email, password };
    if (token) user.token = token;
    if (userId) user.userId = userId;
    if (name) user.name = name;
    if (role) user.role = role;
    localStorage.setItem('user', JSON.stringify(user));
  },

  getUser(): StoredUser | null {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  },

  saveToken(token: string): void {
    const user = this.getUser();
    if (user) {
      user.token = token;
      localStorage.setItem('user', JSON.stringify(user));
    }
  },

  getToken(): string | null {
    const user = this.getUser();
    return user?.token || null;
  },

  setLogged(flag: boolean): void {
    localStorage.setItem('logged', flag ? '1' : '0');
  },

  isLogged(): boolean {
    return localStorage.getItem('logged') === '1';
  },

  clear(): void {
    localStorage.removeItem('user');
    localStorage.removeItem('logged');
  }
};

