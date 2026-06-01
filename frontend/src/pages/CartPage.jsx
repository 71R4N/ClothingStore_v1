import React from 'react';
import { useCart } from '../hooks/useCart';
import { Table, Button, InputNumber, Empty, Typography, Space, Popconfirm, Divider } from 'antd';
import { DeleteOutlined, ShoppingCartOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;

function CartPage() {
  const { items, total, updateQuantity, removeItem, clearCart } = useCart();
  const navigate = useNavigate();

  const columns = [
    {
      title: 'Товар',
      dataIndex: 'product_name',
      key: 'name',
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 500 }}>{text}</div>
          <div style={{ fontSize: 12, color: '#888' }}>Размер: {record.size || '-'}</div>
        </div>
      )
    },
    { title: 'Цена', dataIndex: 'price', key: 'price', render: (price) => `$${(price ?? 0).toFixed(2)}` },
    {
      title: 'Кол-во',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity, record) => (
        <InputNumber min={1} value={quantity} onChange={(val) => updateQuantity(record.id, val)} />
      )
    },
    {
  title: 'Сумма',
  key: 'subtotal',
  render: (_, record) => <span>${((record.price ?? 0) * (record.quantity ?? 0)).toFixed(2)}</span>
},
    {
      title: '',
      key: 'action',
      render: (_, record) => (
        <Popconfirm title="Удалить товар?" onConfirm={() => removeItem(record.id)}>
          <Button type="text" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      )
    }
  ];

  const dataSource = items.map(item => ({
  id: item.id,
  product_name: item.product?.name || `Товар #${item.product_id}`,
  size: item.size?.size_label || '-',
  price: item.product?.price ?? item.price ?? 0,
  quantity: item.quantity,
}));

  if (items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <ShoppingCartOutlined style={{ fontSize: 64, color: '#ddd' }} />
        <Title level={3} style={{ marginTop: 16 }}>Корзина пуста</Title>
        <Button type="primary" onClick={() => navigate('/catalog')}>Перейти к покупкам</Button>
      </div>
    );
  }

  return (
    <>
      <Title level={2} style={{ marginBottom: 24 }}>🛒 Корзина</Title>
      <Table
        dataSource={dataSource}
        columns={columns}
        rowKey="id"
        pagination={false}
        summary={() => (
          <Table.Summary fixed>
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={3} align="right">
                <strong>Итого:</strong>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={1}>
                <span style={{ fontSize: 20, fontWeight: 700, color: '#ff4d4f' }}>${total.toFixed(2)}</span>
              </Table.Summary.Cell>
              <Table.Summary.Cell />
            </Table.Summary.Row>
          </Table.Summary>
        )}
      />
      <Divider />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 16, marginTop: 16 }}>
        <Button onClick={clearCart} size="large">Очистить корзину</Button>
        <Button type="primary" size="large" onClick={() => navigate('/checkout')} icon={<ArrowRightOutlined />}>
          Оформить заказ
        </Button>
      </div>
    </>
  );
}

export default CartPage;