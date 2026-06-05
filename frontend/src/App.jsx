import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import ScrollToTop from './components/ScrollToTop';
import ProtectedRoute from './components/ProtectedRoute';
import HomePage from './pages/HomePage';
import CatalogPage from './pages/CatalogPage';
import ProductPage from './pages/ProductPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import OrdersPage from './pages/OrdersPage';
import OrderDetailPage from './pages/OrderDetailPage';
import TryOnPage from './pages/TryOnPage';
import NotFoundPage from './pages/NotFoundPage';
import WishlistPage from './pages/WishlistPage';
import PaymentStatusPage from './pages/PaymentStatusPage';

function App() {
    return (
        <>
            <ScrollToTop />
            <Layout>
                <Routes>
                    {/* Публичные страницы */}
                    <Route path="/" element={<HomePage />} />
                    <Route path="/catalog" element={<CatalogPage />} />
                    <Route path="/product/:slug" element={<ProductPage />} />
                    <Route path="/cart" element={<CartPage />} />
                    <Route path="/wishlist" element={<WishlistPage />} />
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/register" element={<RegisterPage />} />
                    <Route path="/try-on" element={<TryOnPage />} />
                    <Route path="/checkout" element={<CheckoutPage />} />

                    {/* Страница статуса платежа (возврат с ЮKassa) */}
                    <Route
                        path="/payment/status"
                        element={<PaymentStatusPage />}
                    />

                    {/* Приватные страницы (только для авторизованных) */}
                    <Route
                        path="/profile"
                        element={
                            <ProtectedRoute>
                                <ProfilePage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/orders"
                        element={
                            <ProtectedRoute>
                                <OrdersPage />
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/orders/:id"
                        element={
                            <ProtectedRoute>
                                <OrderDetailPage />
                            </ProtectedRoute>
                        }
                    />

                    {/* 404 — всегда в конце */}
                    <Route path="*" element={<NotFoundPage />} />
                </Routes>
            </Layout>
        </>
    );
}

export default App;