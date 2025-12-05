import { User } from '../types';

export const storage = {
  saveUser(email: string, password: string): void {
    localStorage.setItem('user', JSON.stringify({ email, password }));
  },

  getUser(): User | null {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  },

  setLogged(flag: boolean): void {
    localStorage.setItem('logged', flag ? '1' : '0');
  },

  isLogged(): boolean {
    return localStorage.getItem('logged') === '1';
  }
};

