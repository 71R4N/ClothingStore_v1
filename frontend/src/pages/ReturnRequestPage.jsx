// frontend/src/pages/ReturnRequestPage.jsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { orderService } from '../services/orderService';
import { returnService } from '../services/returnService';
import { uploadService } from '../services/uploadService';
import {
    Typography, Button, Card, Checkbox, InputNumber, Select,
    Input, Upload, message, Spin, Alert, Space, Image, Divider, Progress
} from 'antd';
import {
    ArrowLeftOutlined, UploadOutlined, RotateLeftOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { TextArea } = Input;

const RETURN_REASONS = [
    { value: 'defective', label: 'Брак / дефект товара' },
    { value: 'wrong_size', label: 'Не подошёл размер' },
    { value: 'wrong_color', label: 'Не тот цвет' },
    { value: 'changed_mind', label: 'Передумал(а)' },
    { value: 'other', label: 'Другая причина' },
];

function ReturnRequestPage() {
    const { orderId } = useParams();
    const navigate = useNavigate();
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [progress, setProgress] = useState(0);
    const [selectedItems, setSelectedItems] = useState({});
    const [reason, setReason] = useState(null);
    const [description, setDescription] = useState('');
    const [photos, setPhotos] = useState({});

    useEffect(() => {
        const loadOrder = async () => {
            try {
                const res = await orderService.getOrder(orderId);
                setOrder(res.data);
            } catch (e) {
                message.error('Не удалось загрузить заказ');
                navigate('/orders');
            } finally {
                setLoading(false);
            }
        };
        if (orderId) loadOrder();
    }, [orderId, navigate]);

    const toggleItem = (itemId) => {
        setSelectedItems(prev => {
            const next = { ...prev };
            if (next[itemId]) {
                delete next[itemId];
            } else {
                const item = order.items.find(i => i.id === itemId);
                next[itemId] = {
                    quantity: 1,
                    maxQuantity: item.quantity,
                    price: item.price_at_purchase
                };
            }
            return next;
        });
    };

    const updateQuantity = (itemId, qty) => {
        setSelectedItems(prev => ({
            ...prev,
            [itemId]: { ...prev[itemId], quantity: qty }
        }));
    };

    const handlePhotoUpload = async (itemId, file) => {
        try {
            const res = await uploadService.uploadImage(file);
            setPhotos(prev => ({
                ...prev,
                [itemId]: [...(prev[itemId] || []), res.data.url]
            }));
        } catch (e) {
            message.error('Ошибка загрузки фото');
        }
        return false;
    };

    const calculateTotal = () => {
        return Object.entries(selectedItems).reduce((sum, [id, data]) => {
            return sum + data.quantity * data.price;
        }, 0);
    };

    const handleSubmit = async () => {
        if (!reason) {
            message.warning('Выберите причину возврата');
            return;
        }
        if (Object.keys(selectedItems).length === 0) {
            message.warning('Выберите хотя бы один товар');
            return;
        }

        setSubmitting(true);
        setProgress(0);

        const itemsList = Object.entries(selectedItems);
        const totalItems = itemsList.length;
        let successCount = 0;
        let errorCount = 0;

        // Создаём отдельную заявку для каждого товара
        for (let i = 0; i < itemsList.length; i++) {
            const [orderItemId, data] = itemsList[i];

            try {
                await returnService.createReturn({
                    order_id: orderId,
                    order_item_id: orderItemId,
                    quantity: data.quantity,
                    reason_type: reason,
                    description: description || null,
                    photos: photos[orderItemId] || []
                });
                successCount++;
            } catch (e) {
                errorCount++;
                const itemName = order.items.find(
                    item => item.id === orderItemId
                )?.variant?.product?.name || 'товар';
                message.error(
                    `Ошибка возврата "${itemName}": ${e.response?.data?.detail || 'Неизвестная ошибка'}`
                );
            }

            // Обновляем прогресс
            setProgress(Math.round(((i + 1) / totalItems) * 100));
        }

        setSubmitting(false);

        if (successCount > 0) {
            message.success(
                `Создано заявок: ${successCount} из ${totalItems}`
            );
            navigate('/returns');
        } else {
            message.error('Не удалось создать ни одной заявки');
        }
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: 100 }}>
                <Spin size="large" />
            </div>
        );
    }

    if (!order) return null;

    return (
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate(`/orders/${orderId}`)}
                style={{ marginBottom: 24 }}
            >
                Назад к заказу
            </Button>
            <Title level={2}>
                <RotateLeftOutlined style={{ marginRight: 12 }} />
                Возврат товаров
            </Title>
            <Alert
                message="Каждый товар оформляется как отдельная заявка на возврат"
                description="Это позволяет администратору принимать решения по каждому товару независимо."
                type="info"
                showIcon
                style={{ marginBottom: 24 }}
            />
            <Card title="Выберите товары для возврата" style={{ marginBottom: 24 }}>
                {order.items.map(item => {
                    const isSelected = !!selectedItems[item.id];
                    const variant = item.variant || {};
                    const product = variant.product || {};

                    return (
                        <div
                            key={item.id}
                            style={{
                                padding: 16,
                                border: '1px solid #f0f0f0',
                                borderRadius: 12,
                                marginBottom: 12,
                                background: isSelected ? '#f0f7ff' : '#fff'
                            }}
                        >
                            <Checkbox
                                checked={isSelected}
                                onChange={() => toggleItem(item.id)}
                            >
                                <Space>
                                    <Image
                                        src={variant.image_url || 'https://via.placeholder.com/60'}
                                        width={60} height={80}
                                        style={{ objectFit: 'cover' }}
                                        preview={false}
                                    />
                                    <div>
                                        <Text strong>{product.name}</Text>
                                        <div style={{ fontSize: 12, color: '#888' }}>
                                            {variant.color?.color_name} • {variant.size?.size_label}
                                        </div>
                                        <Text>
                                            Куплено: {item.quantity} шт. × {Number(item.price_at_purchase).toFixed(2)} ₽
                                        </Text>
                                    </div>
                                </Space>
                            </Checkbox>
                            {isSelected && (
                                <div style={{ marginTop: 16, marginLeft: 32 }}>
                                    <Space>
                                        <Text>Количество к возврату:</Text>
                                        <InputNumber
                                            min={1}
                                            max={selectedItems[item.id]?.maxQuantity}
                                            value={selectedItems[item.id]?.quantity}
                                            onChange={(v) => updateQuantity(item.id, v)}
                                        />
                                    </Space>
                                    {reason === 'defective' && (
                                        <div style={{ marginTop: 12 }}>
                                            <Text>Фото дефекта (опционально):</Text>
                                            <Upload
                                                beforeUpload={(file) =>
                                                    handlePhotoUpload(item.id, file)
                                                }
                                                showUploadList={false}
                                                accept="image/*"
                                            >
                                                <Button
                                                    icon={<UploadOutlined />}
                                                    size="small"
                                                    style={{ marginTop: 8 }}
                                                >
                                                    Загрузить фото
                                                </Button>
                                            </Upload>
                                            {(photos[item.id] || []).length > 0 && (
                                                <Space style={{ marginTop: 8 }}>
                                                    {photos[item.id].map((url, i) => (
                                                        <Image key={i} src={url} width={60} />
                                                    ))}
                                                </Space>
                                            )}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    );
                })}
            </Card>
            <Card title="Причина возврата" style={{ marginBottom: 24 }}>
                <Select
                    placeholder="Выберите причину"
                    style={{ width: '100%' }}
                    value={reason}
                    onChange={setReason}
                    options={RETURN_REASONS}
                    size="large"
                />
                <div style={{ marginTop: 16 }}>
                    <Text strong>Комментарий (опционально):</Text>
                    <TextArea
                        rows={3}
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        maxLength={1000}
                        showCount
                        placeholder="Опишите подробнее..."
                        style={{ marginTop: 8 }}
                    />
                </div>
            </Card>
            <Card style={{ marginBottom: 24, background: '#f5f5f5' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong style={{ fontSize: 16 }}>
                        Заявок к созданию: {Object.keys(selectedItems).length}
                    </Text>
                    <Text strong style={{ fontSize: 24, color: '#1890ff' }}>
                        {calculateTotal().toFixed(2)} ₽
                    </Text>
                </div>
                {submitting && (
                    <Progress
                        percent={progress}
                        status="active"
                        style={{ marginTop: 16 }}
                    />
                )}
            </Card>
            <Button
                type="primary"
                size="large"
                block
                loading={submitting}
                onClick={handleSubmit}
                disabled={!reason || Object.keys(selectedItems).length === 0}
            >
                {submitting
                    ? `Создание заявок... ${Object.keys(selectedItems).length} шт.`
                    : `Создать ${Object.keys(selectedItems).length} заявок на возврат`
                }
            </Button>
        </div>
    );
}

export default ReturnRequestPage;