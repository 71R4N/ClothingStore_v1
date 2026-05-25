import React, { useState } from 'react';
import { Form, Input, Button, Typography, message } from 'antd';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

const { Title } = Typography;

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await register(values);
      navigate('/');
    } catch (e) {
      message.error('Ошибка регистрации');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '40px auto' }}>
      <Title level={2}>Регистрация</Title>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="first_name" label="Имя" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="last_name" label="Фамилия" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="Пароль" rules={[{ required: true, min: 6 }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item name="phone" label="Телефон">
          <Input />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Зарегистрироваться
          </Button>
        </Form.Item>
        <Link to="/login">Уже есть аккаунт? Войти</Link>
      </Form>
    </div>
  );
}

export default RegisterPage;