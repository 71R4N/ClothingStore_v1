import React, { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { Typography, Row, Col, Spin, Carousel, Button } from 'antd';
import { RightOutlined, RocketOutlined } from '@ant-design/icons';
import ProductCard from '../components/ProductCard';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

const banners = [
  { title: 'Виртуальная примерка одежды', subtitle: 'Примерьте любую вещь из каталога с помощью нейросети CatVTON', bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', cta: 'Попробовать', link: '/catalog' },
  { title: 'Сезонная распродажа', subtitle: 'Скидки до 40% на коллекцию весна-лето', bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', cta: 'Смотреть', link: '/catalog?discount=true' },
];

function HomePage() {
  const [featured, setFeatured] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    catalogService.getProducts({ limit: 8, sort_by: 'created_at', order: 'desc' })
      .then(res => setFeatured(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      {/* Карусель баннеров */}
      <Carousel autoplay effect="fade" style={{ marginBottom: 48, borderRadius: 24, overflow: 'hidden' }}>
        {banners.map((b, idx) => (
          <div key={idx}>
            <div style={{ background: b.bg, padding: '60px 40px', borderRadius: 24, textAlign: 'center', color: '#fff' }}>
              <Title level={1} style={{ color: '#fff', marginBottom: 16 }}>{b.title}</Title>
              <Paragraph style={{ fontSize: 18, color: '#fff', opacity: 0.9, maxWidth: 600, margin: '0 auto 24px' }}>
                {b.subtitle}
              </Paragraph>
              <Button size="large" ghost onClick={() => navigate(b.link)} icon={<RightOutlined />}>
                {b.cta}
              </Button>
            </div>
          </div>
        ))}
      </Carousel>

      {/* Преимущества */}
      <div style={{ background: '#fff', borderRadius: 24, padding: '32px 24px', marginBottom: 48, boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }}>
        <Row gutter={[24, 24]} justify="center">
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <RocketOutlined style={{ fontSize: 40, color: '#667eea' }} />
            <Title level={4} style={{ marginTop: 12 }}>Быстрая примерка</Title>
            <Text type="secondary">Результат за 30 секунд</Text>
          </Col>
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <img src="/icon-ai.svg" alt="AI" style={{ width: 40, opacity: 0.7 }} onError={e => e.target.style.display='none'} />
            <Title level={4} style={{ marginTop: 12 }}>Нейросеть CatVTON</Title>
            <Text type="secondary">Высокое качество генерации</Text>
          </Col>
          <Col xs={24} sm={8} style={{ textAlign: 'center' }}>
            <img src="/icon-safe.svg" alt="Safe" style={{ width: 40, opacity: 0.7 }} onError={e => e.target.style.display='none'} />
            <Title level={4} style={{ marginTop: 12 }}>Конфиденциальность</Title>
            <Text type="secondary">Ваши фото не сохраняются</Text>
          </Col>
        </Row>
      </div>

      {/* Популярные товары */}
      <Title level={2} style={{ marginBottom: 24 }}>🔥 Популярные товары</Title>
      {loading ? (
        <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
      ) : (
        <Row gutter={[24, 24]}>
          {featured.map(product => (
            <Col key={product.id} xs={24} sm={12} md={8} lg={6}>
              <ProductCard product={product} />
            </Col>
          ))}
        </Row>
      )}
    </>
  );
}

export default HomePage;