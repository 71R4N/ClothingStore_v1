import axios from 'axios';

let accessToken = null;

export const setAccessToken = (token) => {
  accessToken = token;
};

export const getAccessToken = () => accessToken;

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

api.interceptors.request.use(config => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  
  // Добавляем CSRF-токен для небезопасных методов
  if (['post', 'put', 'delete', 'patch'].includes(config.method?.toLowerCase())) {
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
    }
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/refresh') || 
          originalRequest.url?.includes('/auth/login') || 
          originalRequest.url?.includes('/auth/register')) {
        return Promise.reject(error);
      }

      originalRequest._retry = true;
      
      try {
        const response = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true });
        const { access_token } = response.data;
        
        setAccessToken(access_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        return api(originalRequest);
      } catch (refreshError) {
        setAccessToken(null);
        
        const publicPaths = ['/', '/login', '/register', '/catalog', '/product'];
        const currentPath = window.location.pathname;
        
        const isPublic = publicPaths.some(path => 
          currentPath === path || (path !== '/' && currentPath.startsWith(path))
        );
        
        if (!isPublic) {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;