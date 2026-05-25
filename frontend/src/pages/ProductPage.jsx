import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { catalogService } from '../services/catalogService';
import { useCart } from '../hooks/useCart';
import { Typography, Button, Image, Select, Row, Col, Space, Spin } from 'antd';

const { Title, Text } = Typography;

function ProductPage() {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [selectedSize, setSelectedSize] = useState(null);
  const [selectedColor, setSelectedColor] = useState(null);
  const { addToCart } = useCart();

  useEffect(() => {
    catalogService.getProductBySlug(slug)
      .then(res => setProduct(res.data))
      .catch(console.error);
  }, [slug]);

  if (!product) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const mainImg = product.images?.find(i => i.is_main)?.url || product.images?.[0]?.url || 'https://via.placeholder.com/400';

  const handleAddToCart = () => {
    addToCart(product.id, selectedSize, selectedColor, 1);
  };

  return (
    <Row gutter={[24, 24]}>
      <Col xs={24} md={10}>
        <Image src={mainImg} alt={product.name} />
        <div style={{ marginTop: 16 }}>
          {product.images?.filter(i => !i.is_main).map(img => (
            <Image key={img.id} src={img.url} width={80} style={{ marginRight: 8 }} />
          ))}
        </div>
      </Col>
      <Col xs={24} md={14}>
        <Title level={2}>{product.name}</Title>
        <Text type="secondary">{product.brand}</Text>
        <div style={{ marginTop: 16 }}>
          <Text strong style={{ fontSize: '1.8rem', marginRight: 16 }}>${product.price}</Text>
          {product.old_price && <Text delete>${product.old_price}</Text>}
        </div>
        <div style={{ marginTop: 24 }}>
          <Title level={4}>Описание</Title>
          <Text>{product.description}</Text>
        </div>
        <div style={{ marginTop: 24 }}>
          <Space direction="vertical">
            {product.sizes?.length > 0 && (
              <Select
                placeholder="Выберите размер"
                style={{ width: 200 }}
                onChange={setSelectedSize}
              >
                {product.sizes.map(s => (
                  <Select.Option key={s.id} value={s.id} disabled={s.stock_quantity === 0}>
                    {s.size_label} {s.stock_quantity === 0 ? '(нет)' : `(${s.stock_quantity})`}
                  </Select.Option>
                ))}
              </Select>
            )}
            {product.colors?.length > 0 && (
              <Select
                placeholder="Цвет"
                style={{ width: 200 }}
                onChange={setSelectedColor}
              >
                {product.colors.map(c => (
                  <Select.Option key={c.id} value={c.id}>{c.color_name}</Select.Option>
                ))}
              </Select>
            )}
            <Button type="primary" size="large" onClick={handleAddToCart} disabled={product.sizes?.length > 0 && !selectedSize}>
              В корзину
            </Button>
          </Space>
        </div>
      </Col>
    </Row>
  );
}

export default ProductPage;