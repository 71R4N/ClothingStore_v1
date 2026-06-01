import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { tryonService } from '../services/tryonService';
import { catalogService } from '../services/catalogService';
import { Upload, Button, Image, Spin, Typography, Space, Alert, Card, Progress, message } from 'antd';
import { UploadOutlined, CameraOutlined, CheckCircleOutlined, LoadingOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

function TryOnPage() {
  const { productId } = useParams();
  const [searchParams] = useSearchParams();
  const productSlug = searchParams.get('product');
  const [product, setProduct] = useState(null);
  const [personImageFile, setPersonImageFile] = useState(null);
  const [personImagePreview, setPersonImagePreview] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (productSlug) {
      catalogService.getProductBySlug(productSlug)
        .then(res => setProduct(res.data))
        .catch(console.error);
    } else if (productId) {
      catalogService.getProduct(parseInt(productId))
        .then(res => setProduct(res.data))
        .catch(console.error);
    }
  }, [productSlug, productId]);

  const handleUpload = (file) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('Можно загружать только изображения');
      return false;
    }
    setPersonImageFile(file);
    setPersonImagePreview(URL.createObjectURL(file));
    return false;
  };

  const startTryOn = async () => {
    if (!personImageFile || !product) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('product_id', product.id);
    formData.append('person_image', personImageFile);
    try {
      const res = await tryonService.createSession(formData);
      setSessionId(res.data.id);
      message.success('Примерка запущена, ожидайте результат');
      setPolling(true);
      pollSession(res.data.id);
    } catch (e) {
      console.error(e);
      message.error('Ошибка запуска примерки');
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
          message.error('Примерка не удалась');
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
  };

  if (!product) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

  const garmentImage = product.images?.find(i => i.is_main)?.url || product.images?.[0]?.url;

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title level={2}>✨ Виртуальная примерка</Title>
      <Text type="secondary">Загрузите своё фото и примените выбранную вещь</Text>

      <Card style={{ marginTop: 24, borderRadius: 20 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>Выбранный товар:</Text>
            <div style={{ display: 'flex', gap: 16, marginTop: 8, alignItems: 'center' }}>
              <Image src={garmentImage || 'https://via.placeholder.com/100'} width={80} style={{ borderRadius: 12 }} />
              <div>
                <div style={{ fontWeight: 600 }}>{product.name}</div>
                <div style={{ color: '#ff4d4f', fontWeight: 500 }}>${product.price}</div>
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
                <Image src={personImagePreview} width={200} style={{ borderRadius: 16, margin: '16px auto' }} />
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
                  <Text>Нейросеть обрабатывает ваш запрос, это может занять до 30 секунд</Text>
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