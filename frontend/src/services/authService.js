import api from './api';

export const authService = {
  login: (email, password, captcha_response = null) => 
    api.post('/auth/login', { 
      email, 
      password, 
      captcha_response 
    }),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  refresh: () => api.post('/auth/refresh'),
};