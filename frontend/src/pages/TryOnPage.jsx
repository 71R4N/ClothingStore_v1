import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { tryonService } from '../services/tryonService';
import { catalogService } from '../services/catalogService';
import { Upload, Button, Image, Spin, Typography, Space } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const { Title } = Typography;

function TryOnPage() {
  const { productId } = useParams();
  const [searchParams] = useSearchParams();
  const productSlug = searchParams.get('product');
  const [product, setProduct] = useState(null);
  const [personImage, setPersonImage] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [resultImage, setResultImage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (productSlug) {
      catalogService.getProductBySlug(productSlug)
        .then(res => setProduct(res.data))
        .catch(console.error);
    }
  }, [productSlug]);

  const handleUpload = (info) => {
    if (info.file.status === 'done') {
      setPersonImage(URL.createObjectURL(info.file.originFileObj));
    }
  };

  const startTryOn = async () => {
    if (!personImage || !product) return;
    setLoading(true);
    // Здесь должна быть загрузка файла на сервер, но для MVP используем заглушку URL
    const formData = new FormData();
    formData.append('product_id', product.id);
    formData.append('person_image', personImage);  // предполагаем, что сервер примет файл
    try {
      const res = await tryonService.createSession(formData);
      setSessionId(res.data.id);
      pollSession(res.data.id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const pollSession = (id) => {
    const interval = setInterval(async () => {
      const res = await tryonService.getSession(id);
      setSessionStatus(res.data.status);
      if (res.data.status === 'completed') {
        setResultImage(res.data.result_image_url);
        clearInterval(interval);
      } else if (res.data.status === 'failed') {
        clearInterval(interval);
      }
    }, 2000);
  };

  if (!product) return <Spin />;

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <Title level={2}>Виртуальная примерка</Title>
      <p>Товар: <strong>{product.name}</strong></p>
      <Image src={product.images?.[0]?.url || 'https://via.placeholder.com/300'} />
      <div style={{ margin: '24px 0' }}>
        <Upload
          name="person_image"
          showUploadList={false}
          beforeUpload={() => false}
          onChange={handleUpload}
        >
          <Button icon={<UploadOutlined />}>Загрузите своё фото</Button>
        </Upload>
        {personImage && <Image src={personImage} width={200} style={{ marginTop: 16 }} />}
      </div>
      <Button type="primary" onClick={startTryOn} disabled={!personImage} loading={loading}>
        Примерить
      </Button>
      {sessionStatus && <p>Статус: {sessionStatus}</p>}
      {resultImage && <Image src={resultImage} width="100%" style={{ marginTop: 24 }} />}
    </div>
  );
}

export default TryOnPage;