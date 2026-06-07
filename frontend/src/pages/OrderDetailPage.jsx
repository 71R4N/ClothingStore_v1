// frontend/src/pages/OrderDetailPage.jsx
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Descriptions, List, Typography, Spin, Image, Tag, Button, Alert, Space, Divider } from 'antd';
import { ArrowLeftOutlined, RotateLeftOutlined } from '@ant-design/icons';
import { message } from 'antd';

const { Title, Text } = Typography;

function OrderDetailPage() {
    const { id } = useParams();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const returnStatusConfig = {
        pending: { text: 'Оформляется возврат', color: 'gold', textColor: '#000' },
        approved: { text: 'Оформлен возврат', color: 'blue', textColor: '#000' },
        refunded: { text: 'Оформлен возврат', color: 'blue', textColor: '#000' },
        rejected: { text: 'Товар возврату не подлежит', color: 'red', textColor: '#000' },
        failed: { text: 'Ошибка возврата', color: 'volcano' },
        cancelled: { text: 'Возврат отменен', color: 'default' },
    };

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                setLoading(true);
                setError(null);
                const res = await orderService.getOrder(id);
                setOrder(res.data);
            } catch (err) {
                console.error('Failed to fetch order:', err);
                const errorMsg = err.response?.data?.detail || 'Не удалось загрузить информацию о заказе';
                setError(errorMsg);
                message.error(errorMsg);
            } finally {
                setLoading(false);
            }
        };
        if (id) {
            fetchOrder();
        }
    }, [id]);

    const statusColors = {
        pending: 'blue',
        processing: 'orange',
        shipped: 'cyan',
        delivered: 'green',
        cancelled: 'red'
    };

    const statusTexts = {
        pending: 'Ожидает обработки',
        processing: 'В обработке',
        shipped: 'Отправлен',
        delivered: 'Доставлен',
        cancelled: 'Отменён'
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 100 }}>
                <Spin size="large" />
                <div style={{ marginTop: 16 }}>
                    <Text type="secondary">Загрузка информации о заказе...</Text>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div style={{ maxWidth: 800, margin: '0 auto', padding: '40px 24px' }}>
                <Button
                    icon={<ArrowLeftOutlined />}
                    onClick={() => navigate('/orders')}
                    style={{ marginBottom: 24 }}
                >
                    Назад к списку заказов
                </Button>
                <Alert
                    message="Ошибка загрузки"
                    description={error}
                    type="error"
                    showIcon
                    action={
                        <Button size="small" onClick={() => window.location.reload()}>
                            Повторить
                        </Button>
                    }
                />
            </div>
        );
    }

    if (!order) {
        return (
            <div style={{ textAlign: 'center', padding: 100 }}>
                <Title level={3}>Заказ не найден</Title>
                <Button type="primary" onClick={() => navigate('/orders')}>
                    Вернуться к заказам
                </Button>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/orders')}
                style={{ marginBottom: 24 }}
            >
                Назад к списку заказов
            </Button>
            <Title level={2}>
                Заказ #{order.id.substring(0, 8)}
            </Title>
            <Descriptions
                column={{ xs: 1, sm: 2 }}
                bordered
                style={{ marginBottom: 32 }}
            >
                <Descriptions.Item label="Дата создания">
                    {new Date(order.created_at).toLocaleString('ru-RU')}
                </Descriptions.Item>
                <Descriptions.Item label="Статус">
                    <Tag color={statusColors[order.status] || 'default'} style={{ fontSize: 14, padding: '4px 12px' }}>
                        {statusTexts[order.status] || order.status}
                    </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Адрес доставки" span={2}>
                    {order.city}, {order.street}
                </Descriptions.Item>
                {order.guest_email && (
                    <Descriptions.Item label="Email (гостевой заказ)" span={2}>
                        {order.guest_email}
                    </Descriptions.Item>
                )}
                <Descriptions.Item label="Итоговая сумма" span={2}>
                    <Text strong style={{ fontSize: '1.5rem', color: '#1890ff' }}>
                        {Number(order.total).toFixed(2)} ₽
                    </Text>
                </Descriptions.Item>
            </Descriptions>
            <Divider />
            <Title level={4} style={{ marginBottom: 16 }}>
                Состав заказа ({order.items.length} {order.items.length === 1 ? 'товар' : 'товаров'})
            </Title>
            <List
                itemLayout="horizontal"
                dataSource={order.items}
                renderItem={item => {
                    const variant = item.variant || {};
                    const product = variant.product || {};
                    const color = variant.color || {};
                    const size = variant.size || {};

                    const returnCfg = item.return_status ? returnStatusConfig[item.return_status] : null;
                    const isReturned = ['approved', 'refunded'].includes(item.return_status);

                    return (
                        <List.Item
                            style={{
                                padding: '16px',
                                background: isReturned ? '#fff' : '#fff',
                                borderRadius: 8,
                                marginBottom: 12,
                                border: isReturned ? '1px solid #ffe58f' : '1px solid #f0f0f0',
                                display: 'block'
                            }}
                        >
                            <div style={{ display: 'flex', gap: 16 }}>
                                <Image
                                    src={variant.image_url || 'https://via.placeholder.com/100x120?text=No+Image'}
                                    width={100}
                                    height={120}
                                    style={{ objectFit: 'cover', borderRadius: 8 }}
                                    preview={false}
                                    fallback="https://via.placeholder.com/100x120?text=No+Image"
                                />
                                <div style={{ flex: 1 }}>
                                    <Space direction="vertical" size={4} style={{ width: '100%' }}>
                                        <Space wrap>
                                            <Text strong style={{ fontSize: 16 }}>
                                                {product.name || `Товар #${item.variant_id}`}
                                            </Text>
                                            {returnCfg && (
                                                <Tag
                                                    color={returnCfg.color}
                                                    style={{ color: returnCfg.textColor || '#fff', fontWeight: 500 }}
                                                >
                                                    {returnCfg.text}
                                                </Tag>
                                            )}
                                        </Space>
                                        <Text type="secondary" style={{ fontSize: 13 }}>
                                            Артикул: {variant.sku || 'N/A'}
                                        </Text>
                                        <Space direction="vertical" size={2} style={{ marginTop: 4 }}>
                                            {color.color_name && (
                                                <Space size={4}>
                                                    <div style={{
                                                        width: 14, height: 14,
                                                        backgroundColor: color.color_hex,
                                                        borderRadius: '50%',
                                                        border: '1px solid #d9d9d9'
                                                    }} />
                                                    <Text style={{ fontSize: 13 }}>Цвет: {color.color_name}</Text>
                                                </Space>
                                            )}
                                            {size.size_label && (
                                                <Text style={{ fontSize: 13 }}>Размер: {size.size_label}</Text>
                                            )}
                                            <Text style={{ fontSize: 13 }}>Количество: {item.quantity} шт.</Text>
                                        </Space>
                                    </Space>
                                </div>
                                <div style={{ textAlign: 'right', minWidth: 120 }}>
                                    <div style={{ fontSize: 18, fontWeight: 600, color: '#1890ff' }}>
                                        {Number(item.price_at_purchase).toFixed(2)} ₽
                                    </div>
                                    <Text type="secondary" style={{ fontSize: 12 }}>за единицу</Text>
                                    <div style={{ marginTop: 4 }}>
                                        <Text strong>
                                            Итого: {(Number(item.price_at_purchase) * item.quantity).toFixed(2)} ₽
                                        </Text>
                                    </div>
                                </div>
                            </div>
                        </List.Item>
                    );
                }}
            />
            {order.status === 'delivered' && (() => {
                const deliveryDate = new Date(order.updated_at || order.created_at);
                const daysSinceDelivery = (new Date() - deliveryDate) / (1000 * 60 * 60 * 24);
                const allItemsReturned = order.items.every(item =>
                    ['pending', 'approved', 'refunded', 'rejected'].includes(item.return_status)
                );
                const canReturn = daysSinceDelivery <= 14 && !allItemsReturned;

                let buttonText = 'Вернуть товары';
                let tooltip = `Возврат возможен в течение 14 дней с момента доставки (осталось ${Math.max(0, Math.ceil(14 - daysSinceDelivery))} дн.)`;

                if (allItemsReturned) {
                    buttonText = 'Все товары в заявках на возврат';
                    tooltip = 'Для всех товаров в этом заказе уже существуют заявки на возврат';
                } else if (daysSinceDelivery > 14) {
                    buttonText = 'Срок возврата истёк';
                    tooltip = 'Срок возврата (14 дней) истёк';
                }

                return (
                    <div style={{ marginTop: 24 }}>
                        <Button
                            type="primary"
                            size="large"
                            icon={<RotateLeftOutlined />}
                            onClick={() => navigate(`/orders/${order.id}/return`)}
                            disabled={!canReturn}
                            block
                        >
                            {buttonText}
                        </Button>
                        <Text type="secondary" style={{
                            display: 'block', textAlign: 'center',
                            marginTop: 8, fontSize: 12
                        }}>
                            {tooltip}
                        </Text>
                    </div>
                );
            })()}
            {order.status === 'pending' && (
                <Alert
                    message="Заказ ожидает оплаты"
                    description="Вы можете оплатить заказ или отменить его в разделе 'Мои заказы'."
                    type="info"
                    showIcon
                    style={{ marginTop: 24 }}
                />
            )}
        </div>
    );
}

export default OrderDetailPage;