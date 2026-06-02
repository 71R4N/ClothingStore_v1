import api from './api';

export const orderService = {
  createOrder: (data) => api.post('/orders/', data),
  getOrder: (id) => api.get(`/orders/${id}`),
  getUserOrders: () => api.get('/orders/'),
};