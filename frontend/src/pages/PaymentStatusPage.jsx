import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Result, Spin, Button, Typography, Progress, Alert } from 'antd';
import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    LoadingOutlined,
    InfoCircleOutlined
} from '@ant-design/icons';
import { paymentService } from '../services/paymentService';
import { orderService } from '../services/orderService';

const { Paragraph, Text } = Typography;

function PaymentStatusPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const orderId = searchParams.get('order_id');

    const [loading, setLoading] = useState(true);
    const [paymentStatus, setPaymentStatus] = useState(null);
    const [paymentData, setPaymentData] = useState(null);
    const [attempts, setAttempts] = useState(0);
    const [error, setError] = useState(null);

    const MAX_ATTEMPTS = 60;
    const POLL_INTERVAL = 2000;

    const pollStatus = useCallback(async () => {
        if (!orderId) {
            // Если order_id не передан, пытаемся найти последний заказ
            try {
                const ordersRes = await orderService.getUserOrders();
                const orders = ordersRes.data;
                if (orders && orders.length > 0) {
                    // Берем последний заказ со статусом pending
                    const pendingOrder = orders.find(o => o.status === 'pending');
                    if (pendingOrder) {
                        const res = await paymentService.pollOrderPaymentStatus(pendingOrder.id);
                        const data = res.data;
                        setPaymentData(data);
                        setPaymentStatus(data.status);
                        setError(null);

                        if (data.status === 'succeeded' || data.status === 'canceled') {
                            setLoading(false);
                            return true;
                        }
                        setAttempts(prev => prev + 1);
                        return false;
                    }
                }
                setError('Заказ не найден');
                setLoading(false);
                return true;
            } catch (err) {
                console.error('Error fetching orders:', err);
                setError('Не удалось загрузить заказы');
                setLoading(false);
                return true;
            }
        }

        try {
            const res = await paymentService.pollOrderPaymentStatus(orderId);
            const data = res.data;
            setPaymentData(data);
            setPaymentStatus(data.status);
            setError(null);

            if (data.status === 'succeeded' || data.status === 'canceled') {
                setLoading(false);
                return true;
            }

            setAttempts(prev => prev + 1);
            return false;
        } catch (err) {
            console.error('Polling error:', err);
            setAttempts(prev => prev + 1);
            return false;
        }
    }, [orderId]);

    useEffect(() => {
        let isActive = true;
        let intervalId = null;

        const startPolling = async () => {
            const isComplete = await pollStatus();
            if (isComplete || !isActive) return;

            intervalId = setInterval(async () => {
                if (!isActive) {
                    clearInterval(intervalId);
                    return;
                }

                if (attempts >= MAX_ATTEMPTS) {
                    clearInterval(intervalId);
                    setLoading(false);
                    setError('Превышено время ожидания. Проверьте статус заказа позже.');
                    return;
                }

                const complete = await pollStatus();
                if (complete) {
                    clearInterval(intervalId);
                }
            }, POLL_INTERVAL);
        };

        startPolling();

        return () => {
            isActive = false;
            if (intervalId) clearInterval(intervalId);
        };
    }, [attempts, pollStatus]);

    // Состояние загрузки
    if (loading && !error) {
        const progressPercent = Math.min((attempts / MAX_ATTEMPTS) * 100, 99);

        return (
            <div style={{
                textAlign: 'center',
                padding: '80px 24px',
                maxWidth: 600,
                margin: '0 auto'
            }}>
                <Spin
                    indicator={
                        <LoadingOutlined style={{ fontSize: 48 }} spin />
                    }
                />
                <Paragraph style={{ marginTop: 32, fontSize: 18 }}>
                    Проверяем статус платежа...
                </Paragraph>
                <Progress
                    percent={Math.round(progressPercent)}
                    status="active"
                    showInfo={false}
                    style={{ marginTop: 16 }}
                />
                <Text type="secondary">
                    Пожалуйста, не закрывайте страницу
                </Text>
            </div>
        );
    }

    // Ошибка
    if (error) {
        return (
            <div style={{ padding: '60px 24px', maxWidth: 800, margin: '0 auto' }}>
                <Result
                    status="warning"
                    icon={<InfoCircleOutlined style={{ color: '#faad14' }} />}
                    title="Не удалось подтвердить оплату"
                    subTitle={error}
                    extra={[
                        <Button
                            type="primary"
                            key="orders"
                            onClick={() => navigate('/orders')}
                        >
                            Мои заказы
                        </Button>,
                        <Button key="home" onClick={() => navigate('/')}>
                            На главную
                        </Button>,
                    ]}
                />
            </div>
        );
    }

    // Успешная оплата
    if (paymentStatus === 'succeeded') {
        return (
            <div style={{ padding: '60px 24px', maxWidth: 800, margin: '0 auto' }}>
                <Result
                    status="success"
                    title="Оплата прошла успешно!"
                    icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
                    extra={[
                        <Button
                            type="primary"
                            key="orders"
                            onClick={() => navigate('/orders')}
                        >
                            Мои заказы
                        </Button>,
                        <Button key="catalog" onClick={() => navigate('/catalog')}>
                            Продолжить покупки
                        </Button>,
                    ]}
                >
                    <Paragraph>
                        <Text strong style={{ fontSize: 16 }}>
                            Спасибо за покупку в CatVTON Shop!
                        </Text>
                    </Paragraph>
                </Result>
            </div>
        );
    }

    // Отмененная оплата
    if (paymentStatus === 'canceled') {
        return (
            <div style={{ padding: '60px 24px', maxWidth: 800, margin: '0 auto' }}>
                <Result
                    status="error"
                    title="Оплата отменена"
                    subTitle={
                        <>
                            <Paragraph>
                                Процесс оплаты был отменен. Ваш заказ сохранен
                                в системе, вы можете оплатить его позже в разделе
                                «Мои заказы».
                            </Paragraph>
                            {paymentData?.cancellation_reason && (
                                <Text type="secondary">
                                    Причина: {paymentData.cancellation_reason}
                                </Text>
                            )}
                        </>
                    }
                    icon={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
                    extra={[
                        <Button
                            type="primary"
                            key="orders"
                            onClick={() => navigate('/orders')}
                        >
                            Мои заказы
                        </Button>,
                        <Button key="catalog" onClick={() => navigate('/catalog')}>
                            Вернуться в каталог
                        </Button>,
                    ]}
                />
            </div>
        );
    }

    // Неизвестный статус
    return (
        <div style={{ padding: '60px 24px', maxWidth: 800, margin: '0 auto' }}>
            <Result
                status="info"
                title="Статус платежа неизвестен"
                subTitle="Не удалось получить финальный статус. Проверьте заказ позже в разделе «Мои заказы»."
                extra={[
                    <Button
                        type="primary"
                        onClick={() => navigate('/orders')}
                    >
                        Мои заказы
                    </Button>,
                ]}
            />
        </div>
    );
}

export default PaymentStatusPage;