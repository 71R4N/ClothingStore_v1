import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Descriptions, List, Typography, Spin, Image, Tag, Button } from 'antd';

const { Title, Text } = Typography;

function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    orderService.getOrder(id)
      .then(res => setOrder(res.data))
      .catch(err => {
        console.error(err);
        navigate('/orders');
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!order) return null;

  const statusColors = { 
    pending: 'blue', processing: 'orange', shipped: 'cyan', delivered: 'green', cancelled: 'red' 
  };

  return (
    <>
      <Button onClick={() => navigate('/orders')} style={{ marginBottom: 16 }}>← Назад к списку</Button>
      <Title level={2}>Заказ #{order.id.substring(0, 8)}</Title>
      
      <Descriptions column={1} bordered style={{ marginBottom: 24 }}>
        <Descriptions.Item label="Дата создания">{new Date(order.created_at).toLocaleString()}</Descriptions.Item>
        <Descriptions.Item label="Статус">
          <Tag color={statusColors[order.status]}>{order.status}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Адрес доставки">
          {order.city}, {order.street}
        </Descriptions.Item>
        <Descriptions.Item label="Итоговая сумма">
          <Text strong style={{ fontSize: '1.2rem' }}>{Number(order.total).toFixed(2)} ₽</Text>
        </Descriptions.Item>
      </Descriptions>

      <Title level={4}>Состав заказа</Title>
      <List
        itemLayout="horizontal"
        dataSource={order.items}
        renderItem={item => (
          <List.Item>
            <List.Item.Meta
              avatar={
                <Image 
                  src={item.variant?.image_url || 'https://via.placeholder.com/80'} 
                  width={80} 
                  height={100} 
                  style={{ objectFit: 'cover' }}
                  preview={false}
                />
              }
              title={item.variant?.product?.name || `Вариант #${item.variant_id}`}
              description={
                <>
                  <div>Размер: {item.variant?.size?.size_label || '-'}</div>
                  <div>Цвет: {item.variant?.color?.color_name || '-'}</div>
                  <div>Количество: {item.quantity} шт.</div>
                </>
              }
            />
            <div style={{ textAlign: 'right' }}>
              <div>{Number(item.price_at_purchase).toFixed(2)} ₽</div>
              <Text type="secondary">за шт.</Text>
            </div>
          </List.Item>
        )}
      />
    </>
  );
}

export default OrderDetailPage;