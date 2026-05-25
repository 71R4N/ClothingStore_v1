import api from './api';

export const catalogService = {
  getCategories: () => api.get('/catalog/categories/tree'),
  getProducts: (params) => api.get('/catalog/products', { params }),
  getProductBySlug: (slug) => api.get(`/catalog/products/${slug}`),
};