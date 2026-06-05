import api from './api';

export const orderService = {
    createOrder: (data) => api.post('/orders/', data),

    getOrder: (id) => api.get(`/orders/${id}`),

    getUserOrders: () => api.get('/orders/'),

    /**
     * Получает активные заказы (pending, processing, shipped)
     */
    getActiveOrders: () => api.get('/orders/', {
        params: { status_group: 'active' }
    }),

    /**
     * Получает историю заказов (delivered, cancelled)
     */
    getOrderHistory: () => api.get('/orders/', {
        params: { status_group: 'history' }
    }),

    /**
     * Отменяет заказ пользователем (только для статуса pending)
     */
    cancelOrder: (orderId) => api.post(`/orders/${orderId}/cancel`),
};