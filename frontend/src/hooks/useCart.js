import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { cartService } from '../services/cartService';
import { useAuth } from './useAuth';

const CartContext = createContext();

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);

  const fetchCart = useCallback(async () => {
    if (user) {
      try {
        const res = await cartService.getCart();
        setItems(res.data.items);
        setTotal(res.data.total);
      } catch (e) {
        // ignore
      }
    } else {
      // локальная корзина для гостей
      const localCart = JSON.parse(localStorage.getItem('cart') || '[]');
      setItems(localCart);
      calcTotal(localCart);
    }
  }, [user]);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const calcTotal = (cartItems) => {
    const sum = cartItems.reduce((acc, item) => acc + item.price * item.quantity, 0);
    setTotal(sum);
  };

  const addToCart = async (productId, sizeId, colorId, quantity = 1) => {
    if (user) {
      await cartService.addItem({ product_id: productId, size_id: sizeId, color_id: colorId, quantity });
      fetchCart();
    } else {
      const localCart = [...items];
      const existingIndex = localCart.findIndex(
        i => i.product_id === productId && i.size_id === sizeId && i.color_id === colorId
      );
      if (existingIndex > -1) {
        localCart[existingIndex].quantity += quantity;
      } else {
        localCart.push({ product_id: productId, size_id: sizeId, color_id: colorId, quantity, id: Date.now().toString() });
      }
      localStorage.setItem('cart', JSON.stringify(localCart));
      setItems(localCart);
      calcTotal(localCart);
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    if (user) {
      await cartService.updateItem(itemId, quantity);
      fetchCart();
    } else {
      const localCart = items.map(i => i.id === itemId ? { ...i, quantity } : i);
      localStorage.setItem('cart', JSON.stringify(localCart));
      setItems(localCart);
      calcTotal(localCart);
    }
  };

  const removeItem = async (itemId) => {
    if (user) {
      await cartService.removeItem(itemId);
      fetchCart();
    } else {
      const localCart = items.filter(i => i.id !== itemId);
      localStorage.setItem('cart', JSON.stringify(localCart));
      setItems(localCart);
      calcTotal(localCart);
    }
  };

  const clearCart = () => {
    setItems([]);
    setTotal(0);
    if (user) {
      // вызов API очистки корзины (опционально)
    }
    localStorage.removeItem('cart');
  };

  return (
    <CartContext.Provider value={{ items, total, addToCart, updateQuantity, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
