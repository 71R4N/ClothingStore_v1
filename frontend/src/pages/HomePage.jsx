import React, { useEffect, useState } from 'react';
import { catalogService } from '../services/catalogService';
import { Typography, Row, Col, Spin, Button, Card } from 'antd';
import { 
  RocketOutlined, ExperimentOutlined, SafetyCertificateOutlined,
  CameraOutlined, ShoppingOutlined, CheckCircleOutlined,
  ArrowRightOutlined, StarFilled
} from '@ant-design/icons';
import ProductCard from '../components/ProductCard';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;

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
    <div style={{ overflow: 'hidden' }}>
      <section style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        padding: '80px 24px 100px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: -100, right: -100,
          width: 400, height: 400, borderRadius: '50%',
          background: 'rgba(255,255,255,0.1)',
          filter: 'blur(60px)',
        }} />
        <div style={{
          position: 'absolute', bottom: -150, left: -100,
          width: 500, height: 500, borderRadius: '50%',
          background: 'rgba(255,255,255,0.08)',
          filter: 'blur(80px)',
        }} />

        <div style={{ maxWidth: 1200, margin: '0 auto', position: 'relative', zIndex: 1 }}>
          <Row gutter={[48, 48]} align="middle">
            <Col xs={24} lg={14}>
              <div style={{
                display: 'inline-block',
                background: 'rgba(255,255,255,0.2)',
                backdropFilter: 'blur(10px)',
                padding: '8px 20px',
                borderRadius: 20,
                marginBottom: 24,
                color: '#fff',
                fontSize: 14,
                fontWeight: 500,
              }}>
                ✨ Новая технология виртуальной примерки
              </div>
              
              <Title style={{
                color: '#fff',
                fontSize: 'clamp(2.5rem, 5vw, 4rem)',
                fontWeight: 800,
                lineHeight: 1.1,
                marginBottom: 24,
                letterSpacing: '-1px',
              }}>
                Примерь одежду<br />
                <span style={{ 
                  background: 'linear-gradient(90deg, #fff 0%, #ffd6ff 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>не выходя из дома</span>
              </Title>
              
              <Paragraph style={{
                color: 'rgba(255,255,255,0.9)',
                fontSize: 20,
                lineHeight: 1.6,
                marginBottom: 40,
                maxWidth: 500,
              }}>
                Загрузите своё фото и посмотрите, как любая вещь из каталога 
                будет смотреться именно на вас. Нейросеть CatVTON создаст 
                реалистичный образ за 30 секунд.
              </Paragraph>

              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                <Button 
                  size="large" 
                  type="primary"
                  onClick={() => navigate('/catalog')}
                  icon={<ShoppingOutlined />}
                  style={{
                    height: 56,
                    padding: '0 32px',
                    fontSize: 16,
                    fontWeight: 600,
                    borderRadius: 12,
                    background: '#fff',
                    color: '#667eea',
                    border: 'none',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                  }}
                >
                  Перейти в каталог
                </Button>
                <Button 
                  size="large"
                  onClick={() => navigate('/try-on')}
                  icon={<ExperimentOutlined />}
                  style={{
                    height: 56,
                    padding: '0 32px',
                    fontSize: 16,
                    fontWeight: 600,
                    borderRadius: 12,
                    background: 'rgba(255,255,255,0.15)',
                    color: '#fff',
                    border: '2px solid rgba(255,255,255,0.3)',
                    backdropFilter: 'blur(10px)',
                  }}
                >
                  Попробовать примерку
                </Button>
              </div>

              <div style={{ 
                display: 'flex', gap: 32, marginTop: 48, flexWrap: 'wrap',
              }}>
                <div>
                  <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>30 сек</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Среднее время</div>
                </div>
                <div>
                  <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>1000+</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Товаров в каталоге</div>
                </div>
                <div>
                  <div style={{ color: '#fff', fontSize: 28, fontWeight: 700 }}>98%</div>
                  <div style={{ color: 'rgba(255,255,255,0.7)', fontSize: 13 }}>Точность примерки</div>
                </div>
              </div>
            </Col>

            <Col xs={24} lg={10}>
              <div style={{
                background: 'rgba(255,255,255,0.15)',
                backdropFilter: 'blur(20px)',
                borderRadius: 24,
                padding: 24,
                border: '1px solid rgba(255,255,255,0.2)',
                boxShadow: '0 20px 60px rgba(0,0,0,0.2)',
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #fff 0%, #f5f5f5 100%)',
                  borderRadius: 16,
                  padding: 32,
                  textAlign: 'center',
                }}>
                  <ExperimentOutlined style={{ fontSize: 80, color: '#667eea', marginBottom: 16 }} />
                  <Title level={3} style={{ marginBottom: 8 }}>CatVTON AI</Title>
                  <Text type="secondary">
                    Нейросеть нового поколения для виртуальной примерки одежды
                  </Text>
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      <section style={{ padding: '80px 24px', maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <Text type="secondary" style={{ fontSize: 14, fontWeight: 600, letterSpacing: 2, textTransform: 'uppercase' }}>
            Как это работает
          </Text>
          <Title level={1} style={{ marginTop: 12, marginBottom: 16 }}>
            Три простых шага
          </Title>
          <Paragraph style={{ fontSize: 18, color: '#666', maxWidth: 600, margin: '0 auto' }}>
            Виртуальная примерка занимает меньше минуты и не требует специальных навыков
          </Paragraph>
        </div>

        <Row gutter={[32, 32]}>
          {[
            {
              icon: <CameraOutlined />,
              title: 'Загрузите фото',
              description: 'Сделайте фото в полный рост на светлом фоне или используйте готовое изображение',
              color: '#667eea',
              step: '01',
            },
            {
              icon: <ShoppingOutlined />,
              title: 'Выберите одежду',
              description: 'Найдите интересующую вещь в каталоге и выберите нужный размер и цвет',
              color: '#f093fb',
              step: '02',
            },
            {
              icon: <CheckCircleOutlined />,
              title: 'Получите результат',
              description: 'Нейросеть создаст реалистичное изображение вас в выбранной одежде',
              color: '#4facfe',
              step: '03',
            },
          ].map((item, idx) => (
            <Col xs={24} md={8} key={idx}>
              <Card 
                style={{
                  height: '100%',
                  borderRadius: 20,
                  border: 'none',
                  boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer',
                }}
                styles={{ body: { padding: 32 } }}
                onMouseEnter={e => {
                  e.currentTarget.style.transform = 'translateY(-8px)';
                  e.currentTarget.style.boxShadow = '0 12px 40px rgba(0,0,0,0.12)';
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.06)';
                }}
              >
                <div style={{
                  position: 'relative',
                  marginBottom: 24,
                }}>
                  <div style={{
                    width: 72,
                    height: 72,
                    borderRadius: 20,
                    background: `linear-gradient(135deg, ${item.color} 0%, ${item.color}dd 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 32,
                    color: '#fff',
                  }}>
                    {item.icon}
                  </div>
                  <div style={{
                    position: 'absolute',
                    top: -10,
                    right: 20,
                    fontSize: 64,
                    fontWeight: 800,
                    color: 'rgba(0,0,0,0.04)',
                    lineHeight: 1,
                  }}>
                    {item.step}
                  </div>
                </div>
                <Title level={3} style={{ marginBottom: 12 }}>{item.title}</Title>
                <Text type="secondary" style={{ fontSize: 15, lineHeight: 1.6 }}>
                  {item.description}
                </Text>
              </Card>
            </Col>
          ))}
        </Row>
      </section>

      <section style={{ 
        background: 'linear-gradient(180deg, #f8f9ff 0%, #fff 100%)',
        padding: '80px 24px',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 64 }}>
            <Text type="secondary" style={{ fontSize: 14, fontWeight: 600, letterSpacing: 2, textTransform: 'uppercase' }}>
              Почему мы
            </Text>
            <Title level={1} style={{ marginTop: 12 }}>
              Наши преимущества
            </Title>
          </div>

          <Row gutter={[24, 24]}>
            {[
              {
                icon: <RocketOutlined style={{ fontSize: 32 }} />,
                title: 'Быстрая примерка',
                description: 'Результат за 30 секунд благодаря оптимизированной нейросети',
                color: '#667eea',
              },
              {
                icon: <ExperimentOutlined style={{ fontSize: 32 }} />,
                title: 'Технология CatVTON',
                description: 'Передовая модель с точностью генерации до 98%',
                color: '#f093fb',
              },
              {
                icon: <SafetyCertificateOutlined style={{ fontSize: 32 }} />,
                title: 'Конфиденциальность',
                description: 'Ваши фото автоматически удаляются через 24 часа',
                color: '#4facfe',
              },
              {
                icon: <StarFilled style={{ fontSize: 32 }} />,
                title: 'Высокое качество',
                description: 'Реалистичные изображения с учётом фигуры и позы',
                color: '#ffd700',
              },
            ].map((item, idx) => (
              <Col xs={24} sm={12} lg={6} key={idx}>
                <div style={{
                  background: '#fff',
                  padding: 32,
                  borderRadius: 20,
                  height: '100%',
                  boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
                  transition: 'all 0.3s ease',
                  border: '1px solid rgba(0,0,0,0.04)',
                }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.08)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.04)';
                  }}
                >
                  <div style={{
                    width: 64,
                    height: 64,
                    borderRadius: 16,
                    background: `${item.color}15`,
                    color: item.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 20,
                  }}>
                    {item.icon}
                  </div>
                  <Title level={4} style={{ marginBottom: 8 }}>{item.title}</Title>
                  <Text type="secondary" style={{ lineHeight: 1.6 }}>
                    {item.description}
                  </Text>
                </div>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      <section style={{ padding: '80px 24px', maxWidth: 1400, margin: '0 auto' }}>
        <div style={{ 
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginBottom: 40, flexWrap: 'wrap', gap: 16,
        }}>
          <div>
            <Text type="secondary" style={{ fontSize: 14, fontWeight: 600, letterSpacing: 2, textTransform: 'uppercase' }}>
              Каталог
            </Text>
            <Title level={1} style={{ marginTop: 8, marginBottom: 0 }}>
              🔥 Популярные товары
            </Title>
          </div>
          <Button 
            type="link" 
            size="large"
            onClick={() => navigate('/catalog')}
            style={{ fontSize: 16, fontWeight: 500 }}
          >
            Смотреть все <ArrowRightOutlined />
          </Button>
        </div>

        {loading ? (
          <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
        ) : featured.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Text type="secondary">Товары пока не добавлены</Text>
          </div>
        ) : (
          <Row gutter={[24, 24]}>
            {featured.map(product => (
              <Col key={product.id} xs={24} sm={12} md={8} lg={6}>
                <ProductCard product={product} />
              </Col>
            ))}
          </Row>
        )}
      </section>

      <section style={{ padding: '0 24px 80px' }}>
        <div style={{
          maxWidth: 1200,
          margin: '0 auto',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
          borderRadius: 32,
          padding: '64px 48px',
          textAlign: 'center',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', top: -100, right: -100,
            width: 300, height: 300, borderRadius: '50%',
            background: 'rgba(102, 126, 234, 0.2)',
            filter: 'blur(60px)',
          }} />
          
          <div style={{ position: 'relative', zIndex: 1 }}>
            <Title style={{ color: '#fff', fontSize: 'clamp(2rem, 4vw, 3rem)', marginBottom: 16 }}>
              Готовы увидеть себя в новой одежде?
            </Title>
            <Paragraph style={{ color: 'rgba(255,255,255,0.8)', fontSize: 18, marginBottom: 32, maxWidth: 600, margin: '0 auto 32px' }}>
              Попробуйте виртуальную примерку прямо сейчас — это бесплатно и занимает всего 30 секунд
            </Paragraph>
            <Button 
              size="large"
              type="primary"
              onClick={() => navigate('/try-on')}
              icon={<ExperimentOutlined />}
              style={{
                height: 56,
                padding: '0 40px',
                fontSize: 16,
                fontWeight: 600,
                borderRadius: 12,
                background: '#fff',
                color: '#1a1a2e',
                border: 'none',
              }}
            >
              Начать примерку
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;