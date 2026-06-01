import React from 'react';
import { Layout as AntLayout, Menu, Button, Badge, Space, Typography, Drawer, Grid } from 'antd';
import { ShoppingCartOutlined, UserOutlined, HomeOutlined, MenuOutlined, CloseOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';

const { Header, Content, Footer } = AntLayout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

function Layout({ children }) {
  const { user, logout } = useAuth();
  const { items } = useCart();
  const navigate = useNavigate();
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const cartCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const menuItems = [
    { key: 'home', icon: <HomeOutlined />, label: <Link to="/">Главная</Link> },
    { key: 'catalog', label: <Link to="/catalog">Каталог</Link> },
  ];

  const renderMenu = () => (
    <Menu theme="light" mode={isMobile ? 'vertical' : 'horizontal'} items={menuItems} style={{ background: 'transparent', borderBottom: 'none' }} />
  );

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        boxShadow: '0 2px 12px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '100%' }}>
          <div
            onClick={() => navigate('/')}
            style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <img src="/logo.svg" alt="CatVTON" style={{ height: 32 }} onError={(e) => e.target.style.display = 'none'} />
            <Title level={3} style={{ margin: 0, color: '#fff', letterSpacing: '-0.5px' }}>CatVTON</Title>
          </div>

          {!isMobile && (
            <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
              {renderMenu()}
            </div>
          )}

          <Space size={16}>
            <Badge count={cartCount} showZero size="small" offset={[-5, 5]}>
              <Button
                type="text"
                icon={<ShoppingCartOutlined style={{ fontSize: 20, color: '#fff' }} />}
                onClick={() => navigate('/cart')}
                style={{ color: '#fff' }}
              />
            </Badge>
            {user ? (
              <>
                <Button
                  type="text"
                  icon={<UserOutlined style={{ fontSize: 20, color: '#fff' }} />}
                  onClick={() => navigate('/profile')}
                />
                <Button type="link" onClick={logout} style={{ color: '#f0f0f0' }}>Выйти</Button>
              </>
            ) : (
              <Button type="primary" ghost onClick={() => navigate('/login')}>Войти</Button>
            )}
            {isMobile && (
              <Button
                type="text"
                icon={mobileMenuOpen ? <CloseOutlined style={{ color: '#fff' }} /> : <MenuOutlined style={{ color: '#fff' }} />}
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              />
            )}
          </Space>
        </div>
      </Header>

      <Drawer
        placement="left"
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        closable={false}
        bodyStyle={{ padding: 0, background: '#fff' }}
        width="250"
      >
        {renderMenu()}
      </Drawer>

      <Content style={{ padding: '32px 24px', maxWidth: 1400, margin: '0 auto', width: '100%' }}>
        <div className="fade-in-up">
          {children}
        </div>
      </Content>

      <Footer style={{
        textAlign: 'center',
        background: '#f5f5f5',
        borderTop: '1px solid #e8e8e8',
        padding: '24px 16px',
        marginTop: 48
      }}>
        <Text type="secondary">CatVTON Virtual Try-On Shop — примерка одежды с помощью нейросети</Text>
        <div style={{ marginTop: 8 }}>
          <Text type="secondary">© 2026 | Все права защищены</Text>
        </div>
      </Footer>
    </AntLayout>
  );
}

export default Layout;