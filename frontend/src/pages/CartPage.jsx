import React from 'react';
import { useCart } from '../hooks/useCart';
import { Table, Button, InputNumber, Empty, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function CartPage() {
  const { items, total, updateQuantity, removeItem, clearCart } = useCart();
  const navigate = useNavigate();

  const columns = [
    { title: 'Товар', dataIndex: 'product_name', key: 'name' },
    { title: 'Размер', dataIndex: 'size', key: 'size' },
    { title: 'Цена', dataIndex: 'price', key: 'price' },
    {
      title: 'Кол-во',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (_, record) => (
        <InputNumber min={1} value={record.quantity}
          onChange={(val) => updateQuantity(record.id, val)}
        />
      )
    },
    {
      title: 'Действие',
      key: 'action',
      render: (_, record) => (
        <Button danger onClick={() => removeItem(record.id)}>Удалить</Button>
      )
    }
  ];

  const dataSource = items.map(item => ({
    id: item.id,
    product_name: item.product?.name || `Товар #${item.product_id}`,
    size: item.size?.size_label || '-',
    price: item.product?.price || item.price,
    quantity: item.quantity,
  }));

  if (items.length === 0) {
    return <Empty description="Корзина пуста" />;
  }

  return (
    <>
      <Title level={2}>Корзина</Title>
      <Table dataSource={dataSource} columns={columns} rowKey="id" pagination={false} />
      <div style={{ textAlign: 'right', marginTop: 24, fontSize: '1.5rem' }}>
        Итого: ${total.toFixed(2)}
      </div>
      <div style={{ textAlign: 'right', marginTop: 16 }}>
        <Button onClick={clearCart} style={{ marginRight: 16 }}>Очистить корзину</Button>
        <Button type="primary" size="large" onClick={() => navigate('/checkout')}>
          Оформить заказ
        </Button>
      </div>
    </>
  );
}

export default CartPage;