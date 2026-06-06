// frontend/src/services/returnService.js

import api from './api';

export const returnService = {
    /**
     * Создаёт заявку на возврат товаров.
     * @param {Object} data - { order_id, reason_type, description, items }
     */
    createReturn: (data) => api.post('/returns/', data),

    /**
     * Получает список возвратов текущего пользователя.
     */
    getReturns: (params = {}) => api.get('/returns/', { params }),

    /**
     * Получает детальную информацию о возврате.
     */
    getReturn: (returnId) => api.get(`/returns/${returnId}`),

    /**
     * Отменяет заявку на возврат (только статус PENDING).
     */
    cancelReturn: (returnId) => api.post(`/returns/${returnId}/cancel`),

    // ====== Административные методы ======

    /**
     * Получает список возвратов, ожидающих рассмотрения.
     */
    getPendingReturns: (params = {}) =>
        api.get('/returns/admin/pending', { params }),

    /**
     * Одобряет или отклоняет возврат.
     * @param {string} returnId
     * @param {Object} data - { action: 'approve'|'reject', rejection_reason? }
     */
    processReturnAction: (returnId, data) =>
        api.post(`/returns/${returnId}/action`, data),
};