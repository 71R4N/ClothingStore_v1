import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { wishlistService } from '../services/wishlistService';
import { useAuth } from './useAuth';

const WishlistContext = createContext();

export function WishlistProvider({ children }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchWishlist = useCallback(async () => {
    try {
      const res = await wishlistService.getWishlist();
      setItems(res.data || []);
    } catch (e) {
      console.error('Failed to fetch wishlist', e);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWishlist();
  }, [fetchWishlist, user]);

  const addToWishlist = async (variantId) => {
    await wishlistService.addItem(variantId);
    await fetchWishlist();
  };

  const removeFromWishlist = async (variantId) => {
    await wishlistService.removeItem(variantId);
    await fetchWishlist();
  };

  const isInWishlist = (variantId) => {
    return items.some(item => item.variant_id === variantId);
  };

  return (
    <WishlistContext.Provider value={{ 
      items, 
      loading, 
      addToWishlist, 
      removeFromWishlist, 
      isInWishlist,
      fetchWishlist 
    }}>
      {children}
    </WishlistContext.Provider>
  );
}

export const useWishlist = () => useContext(WishlistContext);