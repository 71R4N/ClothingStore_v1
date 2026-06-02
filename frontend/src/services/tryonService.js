import api from './api';

export const tryonService = {
  createSession: (data) => api.post('/try-on/sessions', data),
  getSession: (id) => api.get(`/try-on/sessions/${id}`),
  getUserSessions: () => api.get('/try-on/sessions/'),
};