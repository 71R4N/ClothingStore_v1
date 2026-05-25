import api from './api';

export const cartService = {
  getCart: () => api.get('/cart'),
  addItem: (data) => api.post('/cart/items', data),
  updateItem: (itemId, quantity) => api.patch(`/cart/items/${itemId}`, { quantity }),
  removeItem: (itemId) => api.delete(`/cart/items/${itemId}`),
};