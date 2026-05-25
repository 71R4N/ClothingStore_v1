import React, { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { Typography, Row, Col } from 'antd';
import ProductCard from '../components/ProductCard';

const { Title } = Typography;

function HomePage() {
  const [featured, setFeatured] = useState([]);

  useEffect(() => {
    catalogService.getProducts({ limit: 8, sort_by: 'created_at', order: 'desc' })
      .then(res => setFeatured(res.data))
      .catch(console.error);
  }, []);

  return (
    <>
      <Title level={2}>Популярные товары</Title>
      <Row gutter={[16, 16]}>
        {featured.map(product => (
          <Col key={product.id} xs={24} sm={12} md={8} lg={6}>
            <ProductCard product={product} />
          </Col>
        ))}
      </Row>
    </>
  );
}

export default HomePage;