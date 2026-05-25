import React, { useState } from 'react';
import { Form, Input, Button, Typography, Radio } from 'antd';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../services/orderService';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function CheckoutPage() {
  const { items, total, clearCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    const orderData = {
      guest_email: user ? undefined : values.email,
      shipping_address_id: null,
      payment_method: values.payment_method,
      items: items.map(i => ({ product_id: i.product_id, size_id: i.size_id, color_id: i.color_id, quantity: i.quantity, price_at_purchase: i.price }))
    };
    try {
      const res = await orderService.createOrder(orderData);
      clearCart();
      navigate(`/orders?success=${res.data.id}`);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Title level={2}>Оформление заказа</Title>
      <Form layout="vertical" onFinish={onFinish}>
        {!user && <Form.Item label="Email" name="email" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>}
        <Form.Item label="Способ оплаты" name="payment_method" initialValue="card">
          <Radio.Group>
            <Radio value="card">Банковская карта</Radio>
            <Radio value="tbank">Т-Банк</Radio>
          </Radio.Group>
        </Form.Item>
        <div style={{ fontSize: '1.2rem', marginBottom: 24 }}>Итого к оплате: ${total.toFixed(2)}</div>
        <Button type="primary" htmlType="submit" loading={loading} size="large">
          Оплатить
        </Button>
      </Form>
    </>
  );
}

export default CheckoutPage;