import React from 'react';
import { useWishlist } from '../hooks/useWishlist';
import { Table, Button, Typography, Space, Popconfirm, Image, Empty } from 'antd';
import { DeleteOutlined, HeartOutlined, ShoppingCartOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../hooks/useCart';

const { Title, Text } = Typography;

function WishlistPage() {
  const { items, removeFromWishlist, loading } = useWishlist();
  const { addToCart } = useCart();
  const navigate = useNavigate();

  const columns = [
    {
      title: 'Товар',
      key: 'product',
      render: (_, record) => (
        <Space>
          <Image 
            src={record.variant?.image_url || 'https://via.placeholder.com/60x80'} 
            width={60} 
            height={80} 
            style={{ objectFit: 'cover' }}
            preview={false}
          />
          <div>
            <div style={{ fontWeight: 500 }}>
              {record.variant?.product?.name || `Вариант #${record.variant_id}`}
            </div>
            <div style={{ fontSize: 12, color: '#888' }}>
              {record.variant?.size?.size_label} • {record.variant?.color?.color_name}
            </div>
          </div>
        </Space>
      )
    },
    { 
      title: 'Цена', 
      key: 'price',
      render: (_, record) => `${record.variant?.price?.toFixed(2) || 0} ₽`
    },
    {
      title: 'Наличие',
      key: 'stock',
      render: (_, record) => (
        <Text type={record.variant?.stock_quantity > 0 ? "success" : "danger"}>
          {record.variant?.stock_quantity > 0 ? 'В наличии' : 'Нет в наличии'}
        </Text>
      )
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button 
            type="primary" 
            size="small"
            icon={<ShoppingCartOutlined />}
            onClick={() => {
              addToCart(record.variant_id, 1);
              removeFromWishlist(record.variant_id);
            }}
            disabled={record.variant?.stock_quantity === 0}
          >
            В корзину
          </Button>
          <Popconfirm 
            title="Удалить из избранного?" 
            onConfirm={() => removeFromWishlist(record.variant_id)}
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  if (!loading && items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <HeartOutlined style={{ fontSize: 64, color: '#ddd' }} />
        <Title level={3} style={{ marginTop: 16 }}>В избранном пусто</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          Добавляйте товары в избранное, чтобы не потерять их
        </Text>
        <Button type="primary" onClick={() => navigate('/catalog')}>
          Перейти в каталог
        </Button>
      </div>
    );
  }

  return (
    <>
      <Title level={2} style={{ marginBottom: 24 }}>
        <HeartFilled style={{ color: '#ff4d4f', marginRight: 8 }} />
        Избранное
      </Title>
      <Table
        dataSource={items}
        columns={columns}
        rowKey="id"
        loading={loading}
        pagination={false}
      />
    </>
  );
}

export default WishlistPage;