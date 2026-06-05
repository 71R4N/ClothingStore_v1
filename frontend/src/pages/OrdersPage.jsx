// frontend/src/pages/OrdersPage.jsx
import React, { useEffect, useState, useCallback } from 'react';
import { orderService } from '../services/orderService';
import { cartService } from '../services/cartService';
import { Table, Tag, Button, Typography, Tabs, Space, Modal, message, Spin, Empty } from 'antd';
import {
    ExclamationCircleOutlined,
    ShoppingOutlined,
    CloseCircleOutlined,
    ReloadOutlined
} from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function OrdersPage() {
    const { user } = useAuth();
    const [activeOrders, setActiveOrders] = useState([]);
    const [historyOrders, setHistoryOrders] = useState([]);
    const [activeLoading, setActiveLoading] = useState(true);
    const [historyLoading, setHistoryLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('active');
    const navigate = useNavigate();

    const fetchActiveOrders = useCallback(async () => {
        setActiveLoading(true);
        try {
            const res = await orderService.getActiveOrders();
            setActiveOrders(res.data || []);
        } catch (error) {
            console.error('Failed to fetch active orders:', error);
            message.error('Не удалось загрузить активные заказы');
        } finally {
            setActiveLoading(false);
        }
    }, []);

    const fetchHistoryOrders = useCallback(async () => {
        setHistoryLoading(true);
        try {
            const res = await orderService.getOrderHistory();
            setHistoryOrders(res.data || []);
        } catch (error) {
            console.error('Failed to fetch order history:', error);
            message.error('Не удалось загрузить историю заказов');
        } finally {
            setHistoryLoading(false);
        }
    }, []);

    useEffect(() => {
        if (user) {
            fetchActiveOrders();
            fetchHistoryOrders();
        }
    }, [user, fetchActiveOrders, fetchHistoryOrders]);

    if (!user) {
        return (
            <div style={{ textAlign: 'center', padding: 80 }}>
                <Title level={3}>Войдите, чтобы увидеть свои заказы</Title>
                <Button type="primary" onClick={() => navigate('/login')}>Войти</Button>
            </div>
        );
    }

    const handleCancelOrder = (orderId) => {
        Modal.confirm({
            title: 'Отменить заказ?',
            icon: <ExclamationCircleOutlined />,
            content: 'Вы уверены, что хотите отменить этот заказ? Товары будут возвращены на склад.',
            okText: 'Да, отменить',
            okType: 'danger',
            cancelText: 'Нет',
            onOk: async () => {
                try {
                    await orderService.cancelOrder(orderId);
                    message.success('Заказ успешно отменён');
                    fetchActiveOrders();
                    fetchHistoryOrders();
                } catch (error) {
                    message.error(
                        error.response?.data?.detail || 'Не удалось отменить заказ'
                    );
                }
            },
        });
    };

    const handleRepeatOrder = async (order) => {
        try {
            for (const item of order.items) {
                await cartService.addItem({
                    variant_id: item.variant_id,
                    quantity: item.quantity
                });
            }
            message.success('Товары добавлены в корзину');
            navigate('/cart');
        } catch (error) {
            message.error('Не удалось добавить товары в корзину');
        }
    };

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

    const baseColumns = [
        {
            title: 'Номер заказа',
            dataIndex: 'id',
            key: 'id',
            render: (id) => `#${id.substring(0, 8)}`
        },
        {
            title: 'Дата',
            dataIndex: 'created_at',
            key: 'date',
            render: (date) => new Date(date).toLocaleDateString('ru-RU')
        },
        {
            title: 'Сумма',
            dataIndex: 'total',
            key: 'total',
            render: (total) => `${Number(total).toFixed(2)} ₽`
        },
        {
            title: 'Статус',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Tag color={statusColors[status] || 'default'}>
                    {statusTexts[status] || status}
                </Tag>
            )
        },
    ];

    const activeColumns = [
        ...baseColumns,
        {
            title: 'Действия',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button
                        size="small"
                        onClick={() => navigate(`/orders/${record.id}`)}
                    >
                        Детали
                    </Button>
                    {record.status === 'pending' && (
                        <Button
                            size="small"
                            danger
                            icon={<CloseCircleOutlined />}
                            onClick={() => handleCancelOrder(record.id)}
                        >
                            Отменить
                        </Button>
                    )}
                </Space>
            )
        }
    ];

    const historyColumns = [
        ...baseColumns,
        {
            title: 'Действия',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Button
                        size="small"
                        onClick={() => navigate(`/orders/${record.id}`)}
                    >
                        Детали
                    </Button>
                    {record.status === 'delivered' && (
                        <Button
                            size="small"
                            type="primary"
                            icon={<ReloadOutlined />}
                            onClick={() => handleRepeatOrder(record)}
                        >
                            Повторить
                        </Button>
                    )}
                </Space>
            )
        }
    ];

    const tabItems = [
        {
            key: 'active',
            label: (
                <span>
                    Активные заказы
                    {activeOrders.length > 0 && (
                        <Tag color="blue" style={{ marginLeft: 8 }}>
                            {activeOrders.length}
                        </Tag>
                    )}
                </span>
            ),
            children: activeLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <Spin size="large" />
                </div>
            ) : activeOrders.length === 0 ? (
                <Empty
                    description="Нет активных заказов"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
            ) : (
                <Table
                    dataSource={activeOrders}
                    columns={activeColumns}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                />
            ),
        },
        {
            key: 'history',
            label: (
                <span>
                    История заказов
                    {historyOrders.length > 0 && (
                        <Tag color="default" style={{ marginLeft: 8 }}>
                            {historyOrders.length}
                        </Tag>
                    )}
                </span>
            ),
            children: historyLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <Spin size="large" />
                </div>
            ) : historyOrders.length === 0 ? (
                <Empty
                    description="История заказов пуста"
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                />
            ) : (
                <Table
                    dataSource={historyOrders}
                    columns={historyColumns}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                />
            ),
        },
    ];

    return (
        <div>
            <Title level={2}>
                <ShoppingOutlined style={{ marginRight: 12 }} />
                Мои заказы
            </Title>
            <Tabs
                activeKey={activeTab}
                onChange={setActiveTab}
                items={tabItems}
                size="large"
            />
        </div>
    );
}

export default OrdersPage;