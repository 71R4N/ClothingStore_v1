import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { Descriptions, List, Typography, Spin } from 'antd';

function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    orderService.getOrder(id).then(res => setOrder(res.data)).catch(console.error);
  }, [id]);

  if (!order) return <Spin />;

  return (
    <>
      <Typography.Title level={2}>Заказ #{order.id.substring(0, 8)}</Typography.Title>
      <Descriptions column={1}>
        <Descriptions.Item label="Дата">{new Date(order.created_at).toLocaleString()}</Descriptions.Item>
        <Descriptions.Item label="Статус">{order.status}</Descriptions.Item>
        <Descriptions.Item label="Сумма">${order.total}</Descriptions.Item>
      </Descriptions>
      <List
        header={<div>Товары</div>}
        dataSource={order.items}
        renderItem={item => (
          <List.Item>
            <List.Item.Meta
              title={item.product?.name || `Товар #${item.product_id}`}
              description={`${item.quantity} x $${item.price_at_purchase}`}
            />
          </List.Item>
        )}
      />
    </>
  );
}

export default OrderDetailPage;