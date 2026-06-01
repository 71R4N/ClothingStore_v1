import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,   // ← обязательно для отправки/получения cookie
});

// Функция для получения CSRF-токена из cookie
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Добавляем CSRF-токен в заголовки для небезопасных методов
  if (['post', 'put', 'delete', 'patch'].includes(config.method)) {
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  return config;
});

// Перехватчик для обновления токенов при ошибке 401
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // Запрос на обновление токенов (refresh-токен отправится автоматически в cookie)
        const response = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true });
        const { access_token } = response.data;
        localStorage.setItem('access_token', access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;