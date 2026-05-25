import React from 'react';
import { Card, Button } from 'antd';
import { Link } from 'react-router-dom';
import { useCart } from '../hooks/useCart';

function ProductCard({ product }) {
  const { addToCart } = useCart();
  const mainImage = product.images?.find(img => img.is_main) || product.images?.[0];

  return (
    <Card
      hoverable
      cover={<img alt={product.name} src={mainImage?.url || 'https://via.placeholder.com/300'} />}
      actions={[
        <Button type="primary" onClick={() => addToCart(product.id, null, null, 1)}>В корзину</Button>,
        <Link to={`/try-on/${product.id}`}><Button>Примерка</Button></Link>
      ]}
    >
      <Card.Meta
        title={<Link to={`/product/${product.slug}`}>{product.name}</Link>}
        description={
          <>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>${product.price}</div>
            {product.old_price && <div style={{ textDecoration: 'line-through', color: '#999' }}>${product.old_price}</div>}
          </>
        }
      />
    </Card>
  );
}

export default ProductCard;