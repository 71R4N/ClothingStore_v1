import React from 'react';
import { Card, Tag } from 'antd';
import { Link } from 'react-router-dom';

function ProductCard({ product }) {
  const firstVariant = product.variants?.find(v => v.image_url) || product.variants?.[0];
  const imageUrl = firstVariant?.image_url || 'https://via.placeholder.com/300x400?text=No+Image';
  
  const minPrice = product.variants?.length 
    ? Math.min(...product.variants.map(v => v.price)) 
    : 0;

  const hasStock = product.variants?.some(v => v.stock_quantity > 0);

  return (
    <Link to={`/product/${product.slug}`} style={{ display: 'block', height: '100%' }}>
      <Card
        hoverable
        style={{ height: '100%' }}
        cover={
          <div style={{ position: 'relative' }}>
            <img 
              alt={product.name} 
              src={imageUrl} 
              style={{ height: 300, width: '100%', objectFit: 'cover' }} 
            />
            {!hasStock && (
              <Tag color="red" style={{ position: 'absolute', top: 10, right: 10 }}>
                Нет в наличии
              </Tag>
            )}
          </div>
        }
      >
        <Card.Meta 
          title={product.name} 
          description={
            <div>
              <div style={{ color: '#888', fontSize: 12, marginBottom: 8 }}>
                {product.brand}
              </div>
              <div style={{ fontSize: 18, fontWeight: 'bold', color: '#1890ff' }}>
                от {minPrice.toFixed(0)} ₽
              </div>
            </div>
          } 
        />
      </Card>
    </Link>
  );
}

export default ProductCard;