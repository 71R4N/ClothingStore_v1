import React, { useState } from 'react';
import { Form, Input, Button, Typography, message } from 'antd';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

const { Title } = Typography;

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
      navigate('/');
    } catch (e) {
      message.error('Неверные email или пароль');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: '40px auto' }}>
      <Title level={2}>Вход</Title>
      <Form onFinish={onFinish} layout="vertical">
        <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="password" label="Пароль" rules={[{ required: true }]}>
          <Input.Password />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Войти
          </Button>
        </Form.Item>
        <Link to="/register">Зарегистрироваться</Link>
      </Form>
    </div>
  );
}

export default LoginPage;