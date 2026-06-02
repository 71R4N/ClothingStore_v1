import React from 'react';
import { useCart } from '../hooks/useCart';
import { Table, Button, InputNumber, Typography, Space, Popconfirm, Divider, Image } from 'antd';
import { DeleteOutlined, ShoppingCartOutlined, ArrowRightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function CartPage() {
  const { items, total, updateQuantity, removeItem, clearCart, loading } = useCart();
  const navigate = useNavigate();

  const columns = [
    {
      title: 'Товар',
      key: 'product',
      render: (_, record) => (
        <Space>
          <Image 
            src={record.image} 
            width={60} 
            height={80} 
            style={{ objectFit: 'cover' }}
            preview={false}
          />
          <div>
            <div style={{ fontWeight: 500 }}>{record.product_name}</div>
            <div style={{ fontSize: 12, color: '#888' }}>
              {record.color && <span>Цвет: {record.color} • </span>}
              Размер: {record.size}
            </div>
          </div>
        </Space>
      )
    },
    { 
      title: 'Цена', 
      dataIndex: 'price', 
      key: 'price', 
      render: (price) => `${(price ?? 0).toFixed(2)} ₽` 
    },
    {
      title: 'Кол-во',
      dataIndex: 'quantity',
      key: 'quantity',
      render: (quantity, record) => (
        <InputNumber 
          min={1} 
          value={quantity} 
          onChange={(val) => val && updateQuantity(record.id, val)} 
        />
      )
    },
    {
      title: 'Сумма',
      key: 'subtotal',
      render: (_, record) => <span>{((record.price ?? 0) * (record.quantity ?? 0)).toFixed(2)} ₽</span>
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
    product_name: item.variant?.product?.name || `Вариант #${item.variant_id}`,
    size: item.variant?.size?.size_label || '-',
    color: item.variant?.color?.color_name || '-',
    price: item.variant?.price ?? 0,
    quantity: item.quantity,
    image: item.variant?.image_url || 'https://via.placeholder.com/60x80?text=No+Img',
  }));

  if (!loading && items.length === 0) {
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
        loading={loading}
        summary={() => (
          <Table.Summary fixed>
            <Table.Summary.Row>
              <Table.Summary.Cell index={0} colSpan={3} align="right">
                <strong>Итого:</strong>
              </Table.Summary.Cell>
              <Table.Summary.Cell index={1}>
                <span style={{ fontSize: 20, fontWeight: 700, color: '#ff4d4f' }}>
                  {total.toFixed(2)} ₽
                </span>
              </Table.Summary.Cell>
              <Table.Summary.Cell />
            </Table.Summary.Row>
          </Table.Summary>
        )}
      />
      <Divider />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 16, marginTop: 16 }}>
        <Popconfirm title="Очистить всю корзину?" onConfirm={clearCart}>
          <Button size="large">Очистить корзину</Button>
        </Popconfirm>
        <Button 
          type="primary" 
          size="large" 
          onClick={() => navigate('/checkout')} 
          icon={<ArrowRightOutlined />}
        >
          Оформить заказ
        </Button>
      </div>
    </>
  );
}

export default CartPage;