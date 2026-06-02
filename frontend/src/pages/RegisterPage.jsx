import React, { useState, useMemo } from 'react';
import { Form, Input, Button, Typography, message, Progress, Divider } from 'antd';
import { 
  MailOutlined, LockOutlined, UserOutlined, 
  PhoneOutlined, GoogleOutlined, CheckCircleOutlined 
} from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

const { Title, Text } = Typography;

const getPasswordStrength = (password) => {
  let score = 0;
  if (password.length >= 8) score += 25;
  if (/[A-Z]/.test(password)) score += 25;
  if (/[a-z]/.test(password)) score += 25;
  if (/\d/.test(password)) score += 15;
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 10;
  return Math.min(score, 100);
};

const getStrengthStatus = (strength) => {
  if (strength < 40) return { status: 'exception', color: '#ff4d4f', text: 'Слабый' };
  if (strength < 70) return { status: 'normal', color: '#faad14', text: 'Средний' };
  return { status: 'success', color: '#52c41a', text: 'Надёжный' };
};

function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [password, setPassword] = useState('');
  const [form] = Form.useForm();

  const strength = useMemo(() => getPasswordStrength(password), [password]);
  const strengthInfo = useMemo(() => getStrengthStatus(strength), [strength]);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      await register(values);
      message.success('Добро пожаловать в CatVTON Shop!');
      navigate('/');
    } catch (e) {
      const errors = e.response?.data?.detail;
      if (Array.isArray(errors)) {
        errors.forEach(err => message.error(err.msg || err));
      } else {
        message.error(errors || 'Ошибка регистрации');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      minHeight: 'calc(100vh - 200px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
    }}>
      <div style={{
        width: '100%',
        maxWidth: 1000,
        background: '#fff',
        borderRadius: 24,
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0,0,0,0.1)',
        display: 'flex',
        minHeight: 700,
      }}>
        <div style={{
          flex: 1,
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          padding: 60,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: -50, right: -50,
            width: 200, height: 200, borderRadius: '50%',
            background: 'rgba(255,255,255,0.1)',
          }} />
          <div style={{
            position: 'absolute', bottom: -80, left: -80,
            width: 300, height: 300, borderRadius: '50%',
            background: 'rgba(255,255,255,0.08)',
          }} />

          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{
              width: 80, height: 80, borderRadius: 20,
              background: 'rgba(255,255,255,0.2)',
              backdropFilter: 'blur(10px)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              marginBottom: 32,
            }}>
              <UserOutlined style={{ fontSize: 36, color: '#fff' }} />
            </div>
            
            <Title style={{ color: '#fff', fontSize: 40, marginBottom: 16, fontWeight: 700 }}>
              Присоединяйтесь!
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 18, lineHeight: 1.6, display: 'block', marginBottom: 32 }}>
              Создайте аккаунт и получите доступ к виртуальной примерке одежды с помощью нейросети.
            </Text>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                'Виртуальная примерка за 30 секунд',
                'Персональные рекомендации',
                'История заказов и избранное',
                'Эксклюзивные скидки',
              ].map((item, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <CheckCircleOutlined style={{ color: '#fff', fontSize: 18 }} />
                  <Text style={{ color: '#fff', fontSize: 15 }}>{item}</Text>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div style={{
          flex: 1,
          padding: '48px 48px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          overflowY: 'auto',
        }}>
          <Title level={2} style={{ marginBottom: 8 }}>Создать аккаунт</Title>
          <Text type="secondary" style={{ fontSize: 15, marginBottom: 24, display: 'block' }}>
            Заполните форму для регистрации
          </Text>

          <Form 
            form={form}
            onFinish={onFinish} 
            layout="vertical" 
            size="large"
            requiredMark={false}
          >
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <Form.Item 
                name="first_name" 
                label={<Text strong>Имя</Text>}
                rules={[{ required: true, message: 'Введите имя' }]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                  placeholder="Иван"
                />
              </Form.Item>

              <Form.Item 
                name="last_name" 
                label={<Text strong>Фамилия</Text>}
                rules={[{ required: true, message: 'Введите фамилию' }]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: '#bfbfbf' }} />}
                  placeholder="Иванов"
                />
              </Form.Item>
            </div>

            <Form.Item 
              name="email" 
              label={<Text strong>Email</Text>}
              rules={[
                { required: true, message: 'Введите email' },
                { type: 'email', message: 'Некорректный email' }
              ]}
            >
              <Input 
                prefix={<MailOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="your@email.com"
              />
            </Form.Item>

            <Form.Item 
              name="password" 
              label={<Text strong>Пароль</Text>}
              rules={[
                { required: true, message: 'Введите пароль' },
                { min: 8, message: 'Минимум 8 символов' }
              ]}
              extra={
                password && (
                  <div style={{ marginTop: 8 }}>
                    <Progress 
                      percent={strength} 
                      showInfo={false} 
                      strokeColor={strengthInfo.color}
                      size="small"
                    />
                    <Text style={{ fontSize: 12, color: strengthInfo.color }}>
                      {strengthInfo.text}
                    </Text>
                  </div>
                )
              }
            >
              <Input.Password 
                prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="Минимум 8 символов"
                onChange={(e) => setPassword(e.target.value)}
              />
            </Form.Item>

            <Form.Item 
              name="phone" 
              label={<Text strong>Телефон</Text>}
            >
              <Input 
                prefix={<PhoneOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="+7 (999) 123-45-67"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 16 }}>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading} 
                block
                size="large"
                style={{
                  height: 48,
                  borderRadius: 12,
                  fontWeight: 600,
                  fontSize: 16,
                }}
              >
                Создать аккаунт
              </Button>
            </Form.Item>

            <Divider style={{ margin: '20px 0' }}>
              <Text type="secondary" style={{ fontSize: 13 }}>или</Text>
            </Divider>

            <div style={{ textAlign: 'center', marginTop: 24 }}>
              <Text type="secondary">Уже есть аккаунт? </Text>
              <Link to="/login" style={{ fontWeight: 600 }}>
                Войти
              </Link>
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;