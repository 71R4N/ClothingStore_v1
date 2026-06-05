import React, { useEffect, useState } from 'react';
import { orderService } from '../services/orderService';
import { Table, Tag, Button, Typography } from 'antd';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      orderService.getUserOrders()
        .then(res => setOrders(res.data))
        .catch(console.error)
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user]);

  if (!user) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Title level={3}>Войдите, чтобы увидеть свои заказы</Title>
        <Button type="primary" onClick={() => navigate('/login')}>Войти</Button>
      </div>
    );
  }

  const columns = [
    { title: 'Номер заказа', dataIndex: 'id', key: 'id', render: (id) => `#${id.substring(0, 8)}` },
    { title: 'Дата', dataIndex: 'created_at', key: 'date', render: (date) => new Date(date).toLocaleDateString() },
    { title: 'Сумма', dataIndex: 'total', key: 'total', render: (total) => `${Number(total).toFixed(2)} ₽` },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colorMap = {
          pending: 'blue',
          processing: 'orange',
          shipped: 'cyan',
          delivered: 'green',
          cancelled: 'red'
        };
        const textMap = {
          pending: 'Ожидает обработки',
          processing: 'В обработке',
          shipped: 'Отправлен',
          delivered: 'Доставлен',
          cancelled: 'Отменен'
        };
        return <Tag color={colorMap[status] || 'default'}>{textMap[status] || status}</Tag>;
      }
    },
    {
      title: 'Действие',
      key: 'action',
      render: (_, record) => (
        <Button onClick={() => navigate(`/orders/${record.id}`)}>Детали</Button>
      )
    }
  ];

  return (
    <div>
      <Title level={2}>Мои заказы</Title>
      <Table
        dataSource={orders}
        columns={columns}
        rowKey="id"
        loading={loading}
        locale={{ emptyText: 'У вас пока нет заказов' }}
      />
    </div>
  );
}

export default OrdersPage;