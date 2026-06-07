import React from 'react';
import { useWishlist } from '../hooks/useWishlist';
import { Table, Button, Typography, Space, Popconfirm, Image, Empty, Tag, message } from 'antd';
import { DeleteOutlined, HeartFilled, ShoppingCartOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../hooks/useCart';

const { Title, Text } = Typography;

function WishlistPage() {
  const { items, removeFromWishlist, loading } = useWishlist();
  const { addToCart } = useCart();
  const navigate = useNavigate();

  const handleRemove = async (variantId) => {
    try {
      await removeFromWishlist(variantId);
      message.success('Товар удален из избранного');
    } catch (e) {
      message.error('Ошибка при удалении');
    }
  };

  const handleAddToCart = (variantId) => {
    if (variantId) {
      addToCart(variantId, 1);
      message.success('Добавлено в корзину');
    }
  };

  const columns = [
    {
      title: 'Товар',
      key: 'product',
      render: (_, record) => {
        const variant = record.variant || {};
        const product = variant.product || {};
        const color = variant.color || {};
        
        return (
          <Space>
            <Image 
              src={variant.image_url || 'https://via.placeholder.com/60x80?text=No+Img'} 
              width={60} 
              height={80} 
              style={{ objectFit: 'cover', borderRadius: 4 }}
              preview={false}
            />
            <div>
              <div style={{ fontWeight: 500 }}>
                {product.name || `Товар #${record.variant_id}`}
              </div>
              <div style={{ fontSize: 12, color: '#888' }}>
                {color.color_name && <span>{color.color_name} • </span>}
                Размер: {variant.size?.size_label || '-'}
              </div>
            </div>
          </Space>
        );
      }
    },
    { 
      title: 'Цена', 
      key: 'price',
      render: (_, record) => {
        const price = record.variant?.price;
        return price ? `${Number(price).toFixed(2)} ₽` : '-';
      }
    },
    {
      title: 'Наличие',
      key: 'stock',
      render: (_, record) => {
        const stock = record.variant?.stock_quantity;
        if (stock === undefined) return <Text type="secondary">Нет данных</Text>;
        return (
          <Tag color={stock > 0 ? 'green' : 'red'}>
            {stock > 0 ? `В наличии (${stock})` : 'Нет в наличии'}
          </Tag>
        );
      }
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
            onClick={() => handleAddToCart(record.variant_id)}
            disabled={!record.variant || record.variant.stock_quantity <= 0}
          >
            В корзину
          </Button>
          <Popconfirm 
            title="Удалить из избранного?" 
            onConfirm={() => handleRemove(record.variant_id)} // Удаляем по ID записи в wishlist
            okText="Да"
            cancelText="Нет"
          >
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      )
    }
  ];

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 50 }}>Загрузка...</div>;
  }

  if (!items || items.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <HeartFilled style={{ fontSize: 64, color: '#ff4d4f', marginBottom: 16 }} />
        <Title level={3}>В избранном пусто</Title>
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
        pagination={false}
      />
    </>
  );
}

export default WishlistPage;