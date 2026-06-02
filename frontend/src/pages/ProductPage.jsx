import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { catalogService } from '../services/catalogService';
import { useCart } from '../hooks/useCart';
import { useWishlist } from '../hooks/useWishlist';
import { HeartOutlined, HeartFilled } from '@ant-design/icons';
import { Typography, Button, Image, Select, Row, Col, Space, Spin } from 'antd';

const { Title, Text } = Typography;

function ProductPage() {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [selectedSizeId, setSelectedSizeId] = useState(null);
  const [selectedColorId, setSelectedColorId] = useState(null);
  const { addToCart } = useCart();
  const { addToWishlist, removeFromWishlist, isInWishlist } = useWishlist();

  useEffect(() => {
    catalogService.getProductBySlug(slug)
      .then(res => {
        setProduct(res.data);
        const firstAvailable = res.data.variants?.find(v => v.stock_quantity > 0);
        if (firstAvailable) {
          setSelectedSizeId(firstAvailable.size.id);
          setSelectedColorId(firstAvailable.color.id);
        }
      })
      .catch(console.error);
  }, [slug]);

  const selectedVariant = useMemo(() => {
    if (!product || !selectedSizeId || !selectedColorId) return null;
    return product.variants?.find(
      v => v.size.id === selectedSizeId && v.color.id === selectedColorId
    );
  }, [product, selectedSizeId, selectedColorId]);

  const minPrice = useMemo(() => {
    if (!product?.variants?.length) return 0;
    return Math.min(...product.variants.map(v => v.price));
  }, [product]);

  if (!product) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const mainImg = selectedVariant?.image_url || product.variants?.[0]?.image_url || 'https://via.placeholder.com/400';

  const handleAddToCart = () => {
    if (!selectedVariant) return;
    addToCart(selectedVariant.id, 1); 
  };

  const isSizeAvailable = (sizeId) => {
    if (!selectedColorId) return true;
    return product.variants.some(
      v => v.size.id === sizeId && v.color.id === selectedColorId && v.stock_quantity > 0
    );
  };

  return (
    <Row gutter={[24, 24]}>
      <Col xs={24} md={10}>
        <Image src={mainImg} alt={product.name} style={{ width: '100%' }} />
      </Col>
      <Col xs={24} md={14}>
        <Title level={2}>{product.name}</Title>
        <Text type="secondary">{product.brand}</Text>
        
        <div style={{ marginTop: 16 }}>
          <Text strong style={{ fontSize: '1.8rem', marginRight: 16 }}>
            {/* Показываем цену выбранного варианта или "от X" */}
            {selectedVariant ? selectedVariant.price : `от ${minPrice}`} ₽
          </Text>
        </div>
        
        <div style={{ marginTop: 24 }}>
          <Title level={4}>Описание</Title>
          <Text>{product.description}</Text>
        </div>
        
        <div style={{ marginTop: 24 }}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            
            {/* Выбор цвета */}
            {product.colors?.length > 0 && (
              <div>
                <Text strong>Цвет:</Text>
                <Select
                  placeholder="Выберите цвет"
                  style={{ width: '100%', marginTop: 8 }}
                  value={selectedColorId}
                  onChange={(val) => {
                    setSelectedColorId(val);
                    if (!isSizeAvailable(selectedSizeId)) {
                      setSelectedSizeId(null);
                    }
                  }}
                >
                  {product.colors.map(c => (
                    <Select.Option key={c.id} value={c.id}>
                      <Space>
                        <div style={{ 
                          width: 16, height: 16, 
                          backgroundColor: c.color_hex, 
                          borderRadius: '50%', 
                          border: '1px solid #ccc',
                          display: 'inline-block'
                        }} />
                        {c.color_name}
                      </Space>
                    </Select.Option>
                  ))}
                </Select>
              </div>
            )}

            {/* Выбор размера */}
            {product.sizes?.length > 0 && (
              <div>
                <Text strong>Размер:</Text>
                <Select
                  placeholder="Выберите размер"
                  style={{ width: '100%', marginTop: 8 }}
                  value={selectedSizeId}
                  onChange={setSelectedSizeId}
                >
                  {product.sizes.map(s => (
                    <Select.Option key={s.id} value={s.id} disabled={!isSizeAvailable(s.id)}>
                      {s.size_label} {!isSizeAvailable(s.id) && '(нет в наличии)'}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            )}

            {/* Информация о наличии */}
            {selectedVariant && (
              <Text type={selectedVariant.stock_quantity > 0 ? "success" : "danger"}>
                {selectedVariant.stock_quantity > 0 
                  ? `В наличии: ${selectedVariant.stock_quantity} шт.` 
                  : 'Нет в наличии для выбранной комбинации'}
              </Text>
            )}

            <Button 
              icon={isInWishlist(selectedVariant?.id) ? <HeartFilled style={{color: '#ff4d4f'}} /> : <HeartOutlined />}
              onClick={() => {
                if (isInWishlist(selectedVariant?.id)) {
                  removeFromWishlist(selectedVariant.id);
                } else {
                  addToWishlist(selectedVariant.id);
                }
              }}
              disabled={!selectedVariant}
              size="large"
            >
              {isInWishlist(selectedVariant?.id) ? 'В избранном' : 'В избранное'}
            </Button>
            <Button onClick={() => navigate(`/try-on?variant=${selectedVariant.id}&product=${product.slug}`)}>
              Примерить
            </Button>
            <Button 
              type="primary" 
              size="large" 
              block
              onClick={handleAddToCart} 
              disabled={!selectedVariant || selectedVariant.stock_quantity === 0}
            >
              Добавить в корзину
            </Button>
          </Space>
        </div>
      </Col>
    </Row>
  );
}

export default ProductPage;