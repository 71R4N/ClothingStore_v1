import React, { createContext, useContext, useState, useEffect } from 'react';
import api, { setAccessToken } from '../services/api';
import { authService } from '../services/authService';
import { userService } from '../services/userService';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Инициализация: получаем CSRF + пробуем восстановить сессию
  useEffect(() => {
    const init = async () => {
      try {
        // 1. Получаем CSRF-токен (устанавливается в cookie)
        await api.get('/auth/csrf');
        
        // 2. Пробуем получить текущего пользователя (refresh token из cookie автоматически обновит access)
        const res = await userService.getMe();
        setUser(res.data);
      } catch (e) {
        // Пользователь не авторизован
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  const login = async (email, password) => {
    const res = await authService.login(email, password);
    setAccessToken(res.data.access_token);
    
    const userRes = await userService.getMe();
    setUser(userRes.data);
    return userRes.data;
  };

  const register = async (data) => {
    const res = await authService.register(data);
    setAccessToken(res.data.access_token);
    
    const userRes = await userService.getMe();
    setUser(userRes.data);
    return userRes.data;
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (e) {
      // игнорируем ошибки
    }
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);