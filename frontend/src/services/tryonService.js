import api from './api';

export const tryonService = {
  createSession: (formData) => api.post('/try-on/sessions', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getSession: (id) => api.get(`/try-on/sessions/${id}`),
  getUserSessions: () => api.get('/try-on/sessions'),
};