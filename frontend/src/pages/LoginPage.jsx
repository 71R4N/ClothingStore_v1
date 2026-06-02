import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Typography, message, Divider, Alert } from 'antd';
import { MailOutlined, LockOutlined, GoogleOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { useGoogleReCaptcha } from 'react-google-recaptcha-v3';
import { authService } from '../services/authService';

const { Title, Text } = Typography;

function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [attempts, setAttempts] = useState(0);
  const [form] = Form.useForm();
  const { executeRecaptcha } = useGoogleReCaptcha();

  useEffect(() => {
    if (user) navigate('/');
  }, [user, navigate]);

  useEffect(() => {
    const savedAttempts = sessionStorage.getItem('login_attempts');
    if (savedAttempts) setAttempts(parseInt(savedAttempts));
  }, []);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      let captchaToken = null;
      
      if (attempts >= 3) {
        if (!executeRecaptcha) {
          message.error('reCAPTCHA не загружена. Обновите страницу.');
          return;
        }
        captchaToken = await executeRecaptcha('login');
      }

      const res = await authService.login(values.email, values.password, captchaToken);
      
      setAttempts(0);
      sessionStorage.removeItem('login_attempts');
      
      await login(values.email, values.password);
      
      message.success('Добро пожаловать!');
      navigate('/');
    } catch (e) {
      const newAttempts = attempts + 1;
      setAttempts(newAttempts);
      sessionStorage.setItem('login_attempts', newAttempts.toString());
      
      const errorMsg = e.response?.data?.detail || 'Неверный email или пароль';
      message.error(errorMsg);
      
      if (e.response?.status === 403 && errorMsg.includes('Captcha')) {
        message.warning('Слишком много попыток. Требуется капча.');
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
        minHeight: 600,
      }}>
        {/* Левая часть — визуал */}
        <div style={{
          flex: 1,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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
              <LockOutlined style={{ fontSize: 36, color: '#fff' }} />
            </div>
            
            <Title style={{ color: '#fff', fontSize: 40, marginBottom: 16, fontWeight: 700 }}>
              С возвращением!
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 18, lineHeight: 1.6, display: 'block', marginBottom: 32 }}>
              Войдите в аккаунт, чтобы получить доступ к персональным рекомендациям, истории заказов и виртуальной примерке.
            </Text>

            <div style={{ 
              display: 'flex', gap: 24, flexWrap: 'wrap',
              borderTop: '1px solid rgba(255,255,255,0.2)',
              paddingTop: 32,
            }}>
              <div>
                <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>1000+</div>
                <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Товаров</div>
              </div>
              <div>
                <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>30 сек</div>
                <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Примерка</div>
              </div>
              <div>
                <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>98%</div>
                <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Точность</div>
              </div>
            </div>
          </div>
        </div>

        <div style={{
          flex: 1,
          padding: '60px 48px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}>
          <Title level={2} style={{ marginBottom: 8 }}>Вход в аккаунт</Title>
          <Text type="secondary" style={{ fontSize: 15, marginBottom: 24, display: 'block' }}>
            Введите свои данные для входа
          </Text>

          {attempts >= 3 && (
            <Alert
              message="Требуется дополнительная проверка"
              description="После нескольких неудачных попыток входа требуется пройти проверку безопасности."
              type="warning"
              showIcon
              style={{ marginBottom: 24 }}
            />
          )}

          <Form 
            form={form}
            onFinish={onFinish} 
            layout="vertical" 
            size="large"
            requiredMark={false}
            autoComplete="off"
          >
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
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item 
              name="password" 
              label={<Text strong>Пароль</Text>}
              rules={[{ required: true, message: 'Введите пароль' }]}
            >
              <Input.Password 
                prefix={<LockOutlined style={{ color: '#bfbfbf' }} />}
                placeholder="Введите пароль"
                autoComplete="current-password"
              />
            </Form.Item>

            <div style={{ textAlign: 'right', marginBottom: 24 }}>
              <Link to="/forgot-password" style={{ fontSize: 14 }}>
                Забыли пароль?
              </Link>
            </div>

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
                Войти
              </Button>
            </Form.Item>

            <Divider style={{ margin: '24px 0' }}>
              <Text type="secondary" style={{ fontSize: 13 }}>или</Text>
            </Divider>

            <div style={{ textAlign: 'center', marginTop: 32 }}>
              <Text type="secondary">Нет аккаунта? </Text>
              <Link to="/register" style={{ fontWeight: 600 }}>
                Зарегистрироваться
              </Link>
            </div>
          </Form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;