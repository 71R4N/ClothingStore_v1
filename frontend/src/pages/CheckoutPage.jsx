import React, { useState } from 'react';
import { Form, Input, Button, Typography, Alert } from 'antd';
import { useCart } from '../hooks/useCart';
import { useAuth } from '../hooks/useAuth';
import { orderService } from '../services/orderService';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

function CheckoutPage() {
  const { items, total } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onFinish = async (values) => {
    if (items.length === 0) {
      setError("Ваша корзина пуста");
      return;
    }
    setLoading(true);
    setError(null);
    
    const orderData = {
      guest_email: user ? undefined : values.email,
      street: values.street,
      city: values.city,
    };
    
    try {
      const res = await orderService.createOrder(orderData);
      navigate(`/orders?success=${res.data.id}`);
    } catch (e) {
      console.error(e);
      setError(e.response?.data?.detail || "Ошибка при создании заказа. Проверьте наличие товаров.");
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0 && !loading) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Title level={3}>Ваша корзина пуста</Title>
        <Button type="primary" onClick={() => navigate('/catalog')}>Перейти к покупкам</Button>
      </div>
    );
  }

  return (
    <>
      <Title level={2}>Оформление заказа</Title>
      
      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 24 }} />}

      <Form layout="vertical" onFinish={onFinish} style={{ maxWidth: 600 }}>
        {!user && (
          <Form.Item 
            label="Email (для чека и уведомлений)" 
            name="email" 
            rules={[{ required: true, type: 'email', message: 'Введите корректный email' }]}
          >
            <Input size="large" />
          </Form.Item>
        )}
        
        <Form.Item 
          label="Город" 
          name="city" 
          rules={[{ required: true, message: 'Укажите город' }]}
        >
          <Input size="large" placeholder="Москва" />
        </Form.Item>

        <Form.Item 
          label="Улица, дом и квартира" 
          name="street" 
          rules={[{ required: true, message: 'Укажите адрес доставки' }]}
        >
          <Input size="large" placeholder="ул. Пушкина, д. 10, кв. 5" />
        </Form.Item>

        <div style={{ fontSize: '1.4rem', fontWeight: 'bold', marginBottom: 24, padding: '16px', background: '#f5f5f5', borderRadius: 8 }}>
          Итого к оплате: {total.toFixed(2)} ₽
        </div>
        
        <Button type="primary" htmlType="submit" loading={loading} size="large" block>
          Подтвердить заказ
        </Button>
      </Form>
    </>
  );
}

export default CheckoutPage;