import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { tryonService } from '../services/tryonService';
import { catalogService } from '../services/catalogService';
import { uploadService } from '../services/uploadService';
import { Upload, Button, Image, Spin, Typography, Space, Alert, Card, Progress, message } from 'antd';
import { CameraOutlined, LoadingOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

function TryOnPage() {
  const [searchParams] = useSearchParams();
  const variantId = searchParams.get('variant');
  
  const [variant, setVariant] = useState(null);
  const [product, setProduct] = useState(null);
  const [personImageFile, setPersonImageFile] = useState(null);
  const [personImagePreview, setPersonImagePreview] = useState(null);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (!variantId) return;
    
    const productSlug = searchParams.get('product');
    if (productSlug) {
      catalogService.getProductBySlug(productSlug).then(res => {
        const p = res.data;
        setProduct(p);
        const v = p.variants?.find(v => v.id === parseInt(variantId));
        setVariant(v);
      });
    }
  }, [variantId, searchParams]);

  const handleUpload = (file) => {
    if (!file.type.startsWith('image/')) {
      message.error('Можно загружать только изображения');
      return false;
    }
    setPersonImageFile(file);
    setPersonImagePreview(URL.createObjectURL(file));
    return false;
  };

  const startTryOn = async () => {
    if (!personImageFile || !variant) return;
    setLoading(true);
    
    try {
      const uploadRes = await uploadService.uploadImage(personImageFile);
      const personImageUrl = uploadRes.data.url;

      const res = await tryonService.createSession({
        variant_id: variant.id,
        person_image_url: personImageUrl,
        garment_image_url: variant.image_url,
      });
      
      message.success('Примерка запущена, ожидайте результат');
      setPolling(true);
      pollSession(res.data.id);
    } catch (e) {
      console.error(e);
      message.error(e.response?.data?.detail || 'Ошибка запуска примерки');
    } finally {
      setLoading(false);
    }
  };

  const pollSession = (id) => {
    const interval = setInterval(async () => {
      try {
        const res = await tryonService.getSession(id);
        setSessionStatus(res.data.status);
        
        if (res.data.status === 'completed') {
          setResultImage(res.data.result_image_url);
          setPolling(false);
          clearInterval(interval);
          message.success('Готово! Смотрите результат');
        } else if (res.data.status === 'failed') {
          setPolling(false);
          clearInterval(interval);
          message.error('Примерка не удалась: ' + (res.data.error_message || ''));
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
  };

  if (!variant || !product) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title level={2}>✨ Виртуальная примерка</Title>
      <Text type="secondary">Загрузите своё фото и примените выбранную вещь</Text>

      <Card style={{ marginTop: 24, borderRadius: 20 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>Выбранный товар:</Text>
            <div style={{ display: 'flex', gap: 16, marginTop: 8, alignItems: 'center' }}>
              <Image src={variant.image_url || 'https://via.placeholder.com/100'} width={80} style={{ borderRadius: 12 }} />
              <div>
                <div style={{ fontWeight: 600 }}>{product.name}</div>
                <div style={{ color: '#666' }}>
                  {variant.size?.size_label} • {variant.color?.color_name}
                </div>
                <div style={{ color: '#ff4d4f', fontWeight: 500 }}>{variant.price} ₽</div>
              </div>
            </div>
          </div>

          <div>
            <Text strong>Ваше фото (в полный рост, светлый фон лучше)</Text>
            <Upload.Dragger
              accept="image/*"
              beforeUpload={handleUpload}
              showUploadList={false}
              style={{ marginTop: 8, background: '#fafafa', borderRadius: 16 }}
            >
              {personImagePreview ? (
                <Image src={personImagePreview} width={200} style={{ borderRadius: 16, margin: '16px auto' }} preview={false} />
              ) : (
                <>
                  <CameraOutlined style={{ fontSize: 48, color: '#aaa' }} />
                  <p>Нажмите или перетащите сюда фото</p>
                </>
              )}
            </Upload.Dragger>
          </div>

          <Button
            type="primary"
            size="large"
            onClick={startTryOn}
            disabled={!personImagePreview}
            loading={loading}
            icon={<CameraOutlined />}
            style={{ width: '100%', borderRadius: 40, height: 48 }}
          >
            Примерить
          </Button>

          {polling && (
            <Alert
              message="Обработка"
              description={
                <div>
                  <Progress percent={sessionStatus === 'processing' ? 50 : 10} status="active" showInfo={false} />
                  <Text>Нейросеть CatVTON обрабатывает ваш запрос, это может занять до 30 секунд</Text>
                </div>
              }
              type="info"
              icon={<LoadingOutlined />}
            />
          )}

          {resultImage && (
            <div style={{ marginTop: 16 }}>
              <Text strong>Результат примерки:</Text>
              <div style={{ marginTop: 8, textAlign: 'center' }}>
                <Image src={resultImage} width="100%" style={{ borderRadius: 24, maxHeight: 500, objectFit: 'contain' }} />
              </div>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
}

export default TryOnPage;