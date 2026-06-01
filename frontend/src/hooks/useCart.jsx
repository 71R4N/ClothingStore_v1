import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { cartService } from '../services/cartService';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);

  const fetchCart = useCallback(async () => {
  console.log('🛒 Fetching cart...');
  try {
    const res = await cartService.getCart();
    console.log('✅ Cart loaded:', res.data);
    setItems(res.data.items);
    setTotal(res.data.total);
  } catch (e) {
    console.error('❌ Failed to fetch cart', e);
  }
}, []);

  useEffect(() => {
      localStorage.removeItem('cart');
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (productId, sizeId, colorId, quantity = 1) => {
    await cartService.addItem({ product_id: productId, size_id: sizeId, color_id: colorId, quantity });
    await fetchCart(); // обновим корзину после добавления
  };

  const updateQuantity = async (itemId, quantity) => {
    await cartService.updateItem(itemId, quantity);
    await fetchCart();
  };

  const removeItem = async (itemId) => {
    await cartService.removeItem(itemId);
    await fetchCart();
  };

  const clearCart = async () => {
    // если нужен отдельный эндпоинт очистки – добавить, иначе удалять по одному
    for (const item of items) {
      await cartService.removeItem(item.id);
    }
    await fetchCart();
  };

  return (
    <CartContext.Provider value={{ items, total, addToCart, updateQuantity, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);