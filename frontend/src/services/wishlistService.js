import api from './api';

export const wishlistService = {
  getWishlist: () => api.get('/wishlist/'),
  addItem: (variantId) => api.post('/wishlist/items', { variant_id: variantId }),
  removeItem: (variantId) => api.delete(`/wishlist/items/${variantId}`),
};