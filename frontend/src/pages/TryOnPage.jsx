import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { catalogService } from '../services/catalogService';
import { tryonService } from '../services/tryonService';
import { uploadService } from '../services/uploadService';
import {
  Upload, Button, Image, Spin, Typography, Space, Alert, Card, message, Select, Progress
} from 'antd';
import {
  CameraOutlined, LoadingOutlined, DownloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Dragger } = Upload;

function TryOnPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const variantIdParam = searchParams.get('variant');
  const productSlugParam = searchParams.get('product');

  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [product, setProduct] = useState(null);
  const [selectedVariant, setSelectedVariant] = useState(null);
  const [personImageFile, setPersonImageFile] = useState(null);
  const [personImagePreview, setPersonImagePreview] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    if (!variantIdParam && !productSlugParam) {
      message.warning('Пожалуйста, выберите товар для примерки из каталога');
      return;
    }

    const loadData = async () => {
      setLoading(true);
      try {
        let prodData;
        if (productSlugParam) {
          const res = await catalogService.getProductBySlug(productSlugParam);
          prodData = res.data;
        } else {
          message.error('Некорректные параметры запроса');
          return;
        }

        setProduct(prodData);

        if (variantIdParam) {
          const variant = prodData.variants?.find(v => v.id === parseInt(variantIdParam));
          if (variant) {
            setSelectedVariant(variant);
          } else {
            message.error('Выбранный вариант товара не найден');
          }
        } else if (prodData.variants?.length > 0) {
          setSelectedVariant(prodData.variants[0]);
        }
      } catch (e) {
        console.error(e);
        message.error('Ошибка загрузки данных товара');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [variantIdParam, productSlugParam]);

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
    if (!personImageFile || !selectedVariant) {
      message.warning('Загрузите фото и выберите вариант товара');
      return;
    }

    setSubmitting(true);

    try {
      const uploadRes = await uploadService.uploadImage(personImageFile);

      const res = await tryonService.createSession({
        variant_id: selectedVariant.id,
        person_image_url: uploadRes.data.url,
        garment_image_url: selectedVariant.image_url,
      });

      setSessionId(res.data.id);
      setSessionStatus(res.data.status);
      message.success('Примерка запущена! Обработка может занять до 30 секунд.');

      pollSession(res.data.id);
    } catch (e) {
      console.error(e);
      message.error(e.response?.data?.detail || 'Ошибка запуска примерки');
    } finally {
      setSubmitting(false);
    }
  };

  const pollSession = (id) => {
    setPolling(true);
    const interval = setInterval(async () => {
      try {
        const res = await tryonService.getSession(id);
        setSessionStatus(res.data.status);

        if (res.data.status === 'completed') {
          setResultImage(res.data.result_image_url);
          setPolling(false);
          clearInterval(interval);
          message.success('Готово! Результат примерки получен.');
        } else if (res.data.status === 'failed') {
          setPolling(false);
          clearInterval(interval);
          message.error('Примерка не удалась: ' + (res.data.error_message || 'Неизвестная ошибка'));
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  }

  if (!product || !selectedVariant) {
    return (
      <div style={{ textAlign: 'center', padding: 80 }}>
        <Title level={3}>Товар не выбран</Title>
        <Button type="primary" onClick={() => navigate('/catalog')}>Перейти в каталог</Button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <Title level={2}>✨ Виртуальная примерка</Title>
      <Text type="secondary">Загрузите своё фото и примените выбранную вещь</Text>

      <Card style={{ marginTop: 24, borderRadius: 20 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>Выбранный товар:</Text>
            <div style={{ display: 'flex', gap: 16, marginTop: 8, alignItems: 'center', flexWrap: 'wrap' }}>
              <Image
                src={selectedVariant.image_url || 'https://via.placeholder.com/100'}
                width={80}
                style={{ borderRadius: 12 }}
                preview={false}
              />
              <div>
                <div style={{ fontWeight: 600 }}>{product.name}</div>
                <div style={{ color: '#666', fontSize: 14 }}>
                  {selectedVariant.size?.size_label} • {selectedVariant.color?.color_name}
                </div>
                <div style={{ color: '#ff4d4f', fontWeight: 500 }}>{selectedVariant.price} ₽</div>
              </div>
            </div>

            {product.variants && product.variants.length > 1 && (
              <div style={{ marginTop: 16 }}>
                <Text>Сменить вариант:</Text>
                <Select
                  value={selectedVariant.id}
                  style={{ width: '100%', marginTop: 8 }}
                  onChange={(val) => {
                    const v = product.variants.find(v => v.id === val);
                    if (v) setSelectedVariant(v);
                  }}
                  options={product.variants.map(v => ({
                    label: `${v.size?.size_label} / ${v.color?.color_name}`,
                    value: v.id
                  }))}
                />
              </div>
            )}
          </div>

          <div>
            <Text strong>Ваше фото (в полный рост, светлый фон лучше)</Text>
            <Dragger
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
            </Dragger>
          </div>

          <Button
            type="primary"
            size="large"
            onClick={startTryOn}
            disabled={!personImagePreview || submitting}
            loading={submitting}
            icon={<CameraOutlined />}
            style={{ width: '100%', borderRadius: 40, height: 48 }}
          >
            {submitting ? 'Загрузка...' : 'Примерить'}
          </Button>

          {polling && (
            <Alert
              message="Обработка нейросетью"
              description={
                <div>
                  <Progress percent={sessionStatus === 'processing' ? 50 : 10} status="active" showInfo={false} />
                  <Text>Пожалуйста, подождите. Это может занять до 30 секунд.</Text>
                </div>
              }
              type="info"
              icon={<LoadingOutlined spin />}
              style={{ marginTop: 16 }}
            />
          )}

          {resultImage && (
            <div style={{ marginTop: 16, textAlign: 'center' }}>
              <Text strong>Результат примерки:</Text>
              <div style={{ marginTop: 8 }}>
                <img
                  src={resultImage}
                  alt="Результат примерки"
                  style={{
                    maxWidth: '100%',
                    maxHeight: 500,
                    borderRadius: 24,
                    objectFit: 'contain',
                    display: 'block',
                    margin: '0 auto'
                  }}
                  onError={(e) => {
                    console.error('Failed to load result image:', resultImage);
                    e.target.style.display = 'none';
                    message.error('Не удалось загрузить изображение результата');
                  }}
                />
              </div>
              <Button
                type="link"
                href={resultImage}
                download={`tryon-${sessionId}.png`}
                icon={<DownloadOutlined />}
                style={{ marginTop: 16 }}
              >
                Скачать результат
              </Button>
            </div>
          )}
        </Space>
      </Card>
    </div>
  );
}

export default TryOnPage;