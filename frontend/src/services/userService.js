import api from './api';

export const userService = {
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.patch('/users/me', data),
};
