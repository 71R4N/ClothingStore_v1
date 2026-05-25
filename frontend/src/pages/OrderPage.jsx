import React, { useEffect, useState } from 'react';
import { orderService } from '../services/orderService';
import { Table, Tag, Button } from 'antd';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      orderService.getUserOrders()
        .then(res => setOrders(res.data))
        .catch(console.error);
    }
  }, [user]);

  const columns = [
    { title: 'Номер заказа', dataIndex: 'id', key: 'id', render: (id) => id.substring(0, 8) },
    { title: 'Дата', dataIndex: 'created_at', key: 'date', render: (date) => new Date(date).toLocaleDateString() },
    { title: 'Сумма', dataIndex: 'total', key: 'total', render: (total) => `$${total}` },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const colorMap = { pending: 'blue', paid: 'green', cancelled: 'red', delivered: 'purple' };
        return <Tag color={colorMap[status] || 'default'}>{status}</Tag>;
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
      <h2>Мои заказы</h2>
      <Table dataSource={orders} columns={columns} rowKey="id" />
    </div>
  );
}

export default OrdersPage;