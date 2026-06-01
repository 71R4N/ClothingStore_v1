import React from 'react';
import { Card, Button, Tooltip } from 'antd';
import { ShoppingCartOutlined, EyeOutlined, ExperimentOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { useCart } from '../hooks/useCart';

function ProductCard({ product }) {
  const { addToCart } = useCart();
  const mainImage = product.images?.find(img => img.is_main) || product.images?.[0];
  const price = Number(product.price);
  const oldPrice = product.old_price ? Number(product.old_price) : null;

  const handleAddToCart = (e) => {
    e.preventDefault();
    addToCart(product.id, null, null, 1);
  };

  return (
    <Card
      hoverable
      style={{ borderRadius: 16, overflow: 'hidden', transition: 'all 0.3s ease' }}
      cover={
        <div style={{ position: 'relative', paddingTop: '100%', overflow: 'hidden' }}>
          <img
            alt={product.name}
            src={mainImage?.url || 'https://via.placeholder.com/400?text=No+Image'}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transition: 'transform 0.4s ease',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          />
          {oldPrice && (
            <div style={{
              position: 'absolute',
              top: 12,
              left: 12,
              background: '#ff4d4f',
              color: 'white',
              padding: '4px 8px',
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 600,
              zIndex: 1
            }}>
              -{Math.round((1 - price / oldPrice) * 100)}%
            </div>
          )}
        </div>
      }
      actions={[
        <Tooltip title="Добавить в корзину">
          <Button type="primary" icon={<ShoppingCartOutlined />} onClick={handleAddToCart} size="large" style={{ borderRadius: 30 }}>Купить</Button>
        </Tooltip>,
        <Tooltip title="Виртуальная примерка">
          <Link to={`/try-on/${product.id}?product=${product.slug}`}>
            <Button icon={<ExperimentOutlined />} size="large" style={{ borderRadius: 30 }}>Примерка</Button>
          </Link>
        </Tooltip>,
        <Tooltip title="Подробнее">
          <Link to={`/product/${product.slug}`}>
            <Button icon={<EyeOutlined />} size="large" style={{ borderRadius: 30 }} />
          </Link>
        </Tooltip>
      ]}
      bodyStyle={{ padding: 16 }}
    >
      <Card.Meta
        title={<Link to={`/product/${product.slug}`} style={{ fontWeight: 600, fontSize: 16, color: '#1a1a1a' }}>{product.name}</Link>}
        description={
          <div style={{ marginTop: 8 }}>
            {product.brand && <div style={{ color: '#888', fontSize: 12, marginBottom: 4 }}>{product.brand}</div>}
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
              <span style={{ fontSize: 20, fontWeight: 700, color: '#ff4d4f' }}>${price.toFixed(2)}</span>
              {oldPrice && <span style={{ fontSize: 14, color: '#aaa', textDecoration: 'line-through' }}>${oldPrice.toFixed(2)}</span>}
            </div>
          </div>
        }
      />
    </Card>
  );
}

export default ProductCard;