import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { cartService } from '../services/cartService';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchCart = useCallback(async () => {
    try {
      const res = await cartService.getCart();
      setItems(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (e) {
      console.error('Failed to fetch cart', e);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (variantId, quantity = 1) => {
    try {
      await cartService.addItem({ variant_id: variantId, quantity });
      await fetchCart();
    } catch (e) {
      console.error('Failed to add to cart', e);
      throw e;
    }
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
    await cartService.clearCart();
    await fetchCart();
  };

  return (
    <CartContext.Provider value={{ items, total, loading, addToCart, updateQuantity, removeItem, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);