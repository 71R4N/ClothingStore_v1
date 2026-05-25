import React from 'react';
import { Layout as AntLayout, Menu, Button, Badge, Space, Typography } from 'antd';
import { ShoppingCartOutlined, UserOutlined, HomeOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';

const { Header, Content, Footer } = AntLayout;

function Layout({ children }) {
  const { user, logout } = useAuth();
  const { items } = useCart();
  const navigate = useNavigate();

  const cartCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const menuItems = [
    { key: 'home', icon: <HomeOutlined />, label: <Link to="/">Главная</Link> },
    { key: 'catalog', label: <Link to="/catalog">Каталог</Link> },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="logo" style={{ color: '#fff', fontSize: '1.5rem', fontWeight: 'bold' }}>
          CatVTON
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          items={menuItems}
          style={{ flex: 1, justifyContent: 'flex-end' }}
        />
        <Space>
          <Badge count={cartCount} showZero>
            <Button type="text" icon={<ShoppingCartOutlined style={{ color: '#fff' }} />}
              onClick={() => navigate('/cart')}
            />
          </Badge>
          {user ? (
            <>
              <Button type="text" icon={<UserOutlined style={{ color: '#fff' }} />}
                onClick={() => navigate('/profile')}
              />
              <Button type="link" onClick={logout} style={{ color: '#fff' }}>Выйти</Button>
            </>
          ) : (
            <Button type="link" onClick={() => navigate('/login')} style={{ color: '#fff' }}>
              Войти
            </Button>
          )}
        </Space>
      </Header>
      <Content style={{ padding: '24px', maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        {children}
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        CatVTON Virtual Try-On Shop ©2026
      </Footer>
    </AntLayout>
  );
}

export default Layout;