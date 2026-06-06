import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
    Layout as AntLayout, Menu, Button, Badge, Space, Typography,
    Drawer, Grid, Divider, Dropdown
} from 'antd';
import {
    ShoppingCartOutlined, UserOutlined, HomeOutlined, MenuOutlined,
    CloseOutlined, ShopOutlined, OrderedListOutlined, LoginOutlined,
    LogoutOutlined, ExperimentOutlined, AppstoreOutlined,
    HeartOutlined, HeartFilled, DownOutlined, RotateLeftOutlined
} from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';
import { useCart } from '../hooks/useCart';
import { useWishlist } from '../hooks/useWishlist';
import { catalogService } from '../services/catalogService';

const { Header, Content, Footer } = AntLayout;
const { Title, Text } = Typography;
const { useBreakpoint } = Grid;

function Layout({ children }) {
    const { user, logout } = useAuth();
    const { items } = useCart();
    const { items: wishlistItems } = useWishlist();
    const navigate = useNavigate();
    const location = useLocation();
    const screens = useBreakpoint();
    const isMobile = !screens.md;
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [categories, setCategories] = useState([]);

    useEffect(() => {
        catalogService.getCategories()
            .then(res => setCategories(res.data || []))
            .catch(console.error);
    }, []);

    const cartCount = items.reduce((sum, i) => sum + i.quantity, 0);
    const wishlistCount = wishlistItems ? wishlistItems.length : 0;

    const getSelectedKey = () => {
        const path = location.pathname;
        if (path === '/') return 'home';
        if (path.startsWith('/catalog') || path.startsWith('/product')) return 'catalog';
        if (path.startsWith('/try-on')) return 'tryon';
        if (path.startsWith('/orders')) return 'orders';
        if (path.startsWith('/wishlist')) return 'wishlist';
        return '';
    };

    const categoryMenuItems = categories.map(cat => ({
        key: cat.slug,
        label: <Link to={`/catalog?category_id=${cat.id}`}>{cat.name}</Link>,
        children: cat.children?.length > 0 ? cat.children.map(subcat => ({
            key: subcat.slug,
            label: <Link to={`/catalog?category_id=${subcat.id}`}>{subcat.name}</Link>,
        })) : undefined,
    }));

    const mainMenuItems = [
        {
            key: 'home',
            label: <Link to="/" className="nav-link">Главная</Link>
        },
        {
            key: 'catalog',
            label: (
                <Dropdown
                    menu={{ items: categoryMenuItems }}
                    trigger={['hover']}
                    overlayStyle={{ maxHeight: 400, overflowY: 'auto' }}
                >
                    <span className="nav-link" style={{ cursor: 'pointer' }}>
                        Каталог <DownOutlined style={{ fontSize: 10, marginLeft: 4 }} />
                    </span>
                </Dropdown>
            ),
        },
        {
            key: 'tryon',
            label: <Link to="/try-on" className="nav-link">Примерка</Link>
        },
    ];

    const handleMenuClick = () => {
        setMobileMenuOpen(false);
    };

    const renderDesktopMenu = () => (
        <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[getSelectedKey()]}
            items={mainMenuItems}
            className="desktop-menu"
            style={{
                background: 'transparent',
                borderBottom: 'none',
                flex: 1,
            }}
        />
    );

    const renderMobileMenu = () => {
        const categoryItems = categories.flatMap(cat => [
            {
                key: `cat-${cat.id}`,
                label: <Link to={`/catalog?category_id=${cat.id}`} onClick={handleMenuClick}>{cat.name}</Link>,
                icon: <AppstoreOutlined />
            },
            ...(cat.children?.map(subcat => ({
                key: `subcat-${subcat.id}`,
                label: <Link to={`/catalog?category_id=${subcat.id}`} onClick={handleMenuClick} style={{ paddingLeft: 24 }}>
                    └ {subcat.name}
                </Link>,
            })) || []),
        ]);

        const mobileItems = [
            ...mainMenuItems,
            { type: 'divider' },
            ...(categories.length > 0 ? [
                {
                    key: 'categories-header',
                    label: <Text strong style={{ fontSize: 12, color: '#888', textTransform: 'uppercase' }}>Категории</Text>,
                    disabled: true,
                },
                ...categoryItems,
                { type: 'divider' },
            ] : []),
            ...(user ? [
                {
                    key: 'profile',
                    icon: <UserOutlined />,
                    label: <Link to="/profile" onClick={handleMenuClick}>Личный кабинет</Link>
                },
                {
                    key: 'orders',
                    icon: <OrderedListOutlined />,
                    label: <Link to="/orders" onClick={handleMenuClick}>Мои заказы</Link>
                },
                {
                    key: 'returns',
                    icon: <RotateLeftOutlined />,
                    label: <Link to="/returns" onClick={handleMenuClick}>Мои возвраты</Link>
                },
                {
                    key: 'wishlist',
                    icon: <HeartOutlined />,
                    label: <Link to="/wishlist" onClick={handleMenuClick}>Избранное</Link>
                },
                { type: 'divider' },
                {
                    key: 'logout',
                    icon: <LogoutOutlined />,
                    label: 'Выйти',
                    onClick: () => {
                        handleMenuClick();
                        logout();
                    }
                },
            ] : [
                {
                    key: 'login',
                    icon: <LoginOutlined />,
                    label: <Link to="/login" onClick={handleMenuClick}>Войти</Link>
                },
            ]),
        ];

        return (
            <Menu
                theme="light"
                mode="vertical"
                selectedKeys={[getSelectedKey()]}
                items={mobileItems}
                style={{ borderRight: 'none' }}
            />
        );
    };

    return (
        <AntLayout style={{ minHeight: '100vh' }}>
            {/* ===== HEADER ===== */}
            <Header style={{
                background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
                padding: '0 24px',
                position: 'sticky',
                top: 0,
                zIndex: 100,
                boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
                height: 64,
                display: 'flex',
                alignItems: 'center',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    {/* Логотип */}
                    <div onClick={() => navigate('/')} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8, marginRight: 48 }}>
                        <ExperimentOutlined style={{ fontSize: 28, color: '#1890ff' }} />
                        <Title level={3} style={{ margin: 0, color: '#fff', letterSpacing: '-0.5px', lineHeight: '64px' }}>
                            CatVTON
                        </Title>
                    </div>

                    {/* Меню по центру */}
                    {!isMobile && (
                        <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
                            {renderDesktopMenu()}
                        </div>
                    )}

                    {/* Правая часть: корзина, избранное, заказы, профиль */}
                    <Space size={isMobile ? 8 : 24} align="center">
                        {/* Избранное */}
                        <Badge
                            count={wishlistCount}
                            showZero={false}
                            size="small"
                            offset={[-5, 5]}
                        >
                            <Button
                                type="text"
                                icon={<HeartOutlined style={{ fontSize: 20, color: '#fff' }} />}
                                onClick={() => navigate('/wishlist')}
                                title="Избранное"
                            />
                        </Badge>

                        {/* Корзина */}
                        <Badge
                            count={cartCount}
                            showZero={false}
                            size="small"
                            offset={[-5, 5]}
                        >
                            <Button
                                type="text"
                                icon={<ShoppingCartOutlined style={{ fontSize: 20, color: '#fff' }} />}
                                onClick={() => navigate('/cart')}
                                title="Корзина"
                            />
                        </Badge>

                        {/* Десктоп: заказы, профиль и выход (только для авторизованных) */}
                        {!isMobile && (
                            <>
                                {user ? (
                                    <>
                                        {/* ✅ Иконка заказов — между корзиной и профилем */}
                                        <Button
                                            type="text"
                                            icon={<OrderedListOutlined style={{ fontSize: 20, color: '#fff' }} />}
                                            onClick={() => navigate('/orders')}
                                            title="Мои заказы"
                                        />
                                        <Button
                                            type="text"
                                            icon={<RotateLeftOutlined style={{ fontSize: 20, color: '#fff' }} />}
                                            onClick={() => navigate('/returns')}
                                            title="Мои возвраты"
                                        />
                                        <Button
                                            type="text"
                                            icon={<UserOutlined style={{ fontSize: 20, color: '#fff' }} />}
                                            onClick={() => navigate('/profile')}
                                            title="Личный кабинет"
                                        />
                                        <Button
                                            type="text"
                                            icon={<LogoutOutlined style={{ color: '#fff' }} />}
                                            onClick={logout}
                                            style={{ color: '#f0f0f0' }}
                                        >
                                            Выйти
                                        </Button>
                                    </>
                                ) : (
                                    <Button type="primary" ghost onClick={() => navigate('/login')}>
                                        Войти
                                    </Button>
                                )}
                            </>
                        )}

                        {/* Мобильное: кнопка меню */}
                        {isMobile && (
                            <Button
                                type="text"
                                icon={mobileMenuOpen
                                    ? <CloseOutlined style={{ color: '#fff' }} />
                                    : <MenuOutlined style={{ color: '#fff' }} />
                                }
                                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            />
                        )}
                    </Space>
                </div>
            </Header>

            {/* ===== МОБИЛЬНОЕ МЕНЮ ===== */}
            <Drawer
                placement="left"
                open={mobileMenuOpen}
                onClose={() => setMobileMenuOpen(false)}
                closable={false}
                styles={{ body: { padding: 0, background: '#fff' } }}
                width={280}
            >
                {user && (
                    <div style={{ padding: '24px 16px', borderBottom: '1px solid #f0f0f0' }}>
                        <Space direction="vertical" size={4}>
                            <Text strong>{user.first_name} {user.last_name}</Text>
                            <Text type="secondary" style={{ fontSize: 12 }}>{user.email}</Text>
                        </Space>
                    </div>
                )}
                {renderMobileMenu()}
            </Drawer>

            {/* ===== CONTENT ===== */}
            <Content style={{ padding: '32px 24px', maxWidth: 1400, margin: '0 auto', width: '100%' }}>
                <div className="fade-in-up">
                    {children}
                </div>
            </Content>

            {/* ===== FOOTER ===== */}
            <Footer style={{
                textAlign: 'center',
                background: '#f5f5f5',
                borderTop: '1px solid #e8e8e8',
                padding: '24px 16px',
                marginTop: 48
            }}>
                <Text type="secondary">
                    CatVTON Virtual Try-On Shop — примерка одежды с помощью нейросети
                </Text>
                <div style={{ marginTop: 8 }}>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                        © 2026 | Все права защищены
                    </Text>
                </div>
            </Footer>
        </AntLayout>
    );
}

export default Layout;