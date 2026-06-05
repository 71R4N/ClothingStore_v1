import api from './api';

export const paymentService = {
    /**
     * Инициирует платеж для заказа.
     * @param {string} orderId - ID заказа
     * @returns {Promise} - Ответ с confirmation_url
     */
    initiatePayment: (orderId) =>
        api.post('/payments/initiate', { order_id: orderId }),

    /**
     * Получает информацию о платеже.
     * @param {string} paymentId - ID платежа
     */
    getPayment: (paymentId) =>
        api.get(`/payments/${paymentId}`),

    /**
     * Получает все платежи для заказа.
     * @param {string} orderId - ID заказа
     */
    getOrderPayments: (orderId) =>
        api.get(`/payments/order/${orderId}`),

    /**
     * Отменяет платеж.
     * @param {string} paymentId - ID платежа
     */
    cancelPayment: (paymentId) =>
        api.post(`/payments/${paymentId}/cancel`),

    /**
     * Polling статуса платежа для заказа.
     * @param {string} orderId - ID заказа
     */
    pollOrderPaymentStatus: (orderId) =>
        api.get(`/payments/order/${orderId}/status`),
};
