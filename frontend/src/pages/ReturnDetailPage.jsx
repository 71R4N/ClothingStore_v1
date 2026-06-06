// frontend/src/pages/ReturnDetailPage.jsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { returnService } from '../services/returnService';
import {
    Typography, Card, Descriptions, Tag, Button, Steps,
    Image, List, Spin, Alert, Space, Divider
} from 'antd';
import {
    ArrowLeftOutlined, CheckCircleOutlined,
    CloseCircleOutlined, ClockCircleOutlined, LoadingOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

const REASON_LABELS = {
    defective: 'Брак / дефект',
    wrong_size: 'Не подошёл размер',
    wrong_color: 'Не тот цвет',
    changed_mind: 'Передумал(а)',
    other: 'Другая причина',
};

function ReturnDetailPage() {
    const { returnId } = useParams();
    const navigate = useNavigate();
    const [ret, setRet] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const res = await returnService.getReturn(returnId);
                setRet(res.data);
            } catch (e) {
                navigate('/returns');
            } finally {
                setLoading(false);
            }
        };
        if (returnId) load();
    }, [returnId, navigate]);

    const getStepsStatus = (status) => {
        switch (status) {
            case 'pending':  return 0;
            case 'approved': return 1;
            case 'refunded': return 2;
            case 'rejected':
            case 'cancelled':
            case 'failed':   return 2;
            default:         return 0;
        }
    };

    const getStepStatus = (status) => {
        if (['rejected', 'cancelled', 'failed'].includes(status)) return 'error';
        if (status === 'refunded') return 'finish';
        return 'process';
    };

    if (loading) {
        return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>;
    }

    if (!ret) return null;

    return (
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
            <Button
                icon={<ArrowLeftOutlined />}
                onClick={() => navigate('/returns')}
                style={{ marginBottom: 24 }}
            >
                Назад к возвратам
            </Button>

            <Title level={2}>
                Заявка на возврат #{ret.id.substring(0, 8)}
            </Title>

            <Steps
                current={getStepsStatus(ret.status)}
                status={getStepStatus(ret.status)}
                style={{ marginBottom: 32 }}
                items={[
                    {
                        title: 'Заявка создана',
                        description: new Date(ret.created_at).toLocaleDateString('ru-RU'),
                        icon: <CheckCircleOutlined />
                    },
                    {
                        title: 'На рассмотрении',
                        icon: <ClockCircleOutlined />
                    },
                    {
                        title: ret.status === 'refunded' ? 'Средства возвращены'
                            : ret.status === 'rejected' ? 'Отклонено'
                            : ret.status === 'cancelled' ? 'Отменено'
                            : 'Завершено',
                        icon: ret.status === 'refunded' ? <CheckCircleOutlined />
                            : ['rejected', 'cancelled', 'failed'].includes(ret.status)
                                ? <CloseCircleOutlined />
                                : <LoadingOutlined />
                    }
                ]}
            />

            <Card style={{ marginBottom: 24 }}>
                <Descriptions column={{ xs: 1, sm: 2 }} bordered>
                    <Descriptions.Item label="Статус">
                        <Tag color={
                            ret.status === 'pending' ? 'blue' :
                            ret.status === 'approved' ? 'green' :
                            ret.status === 'refunded' ? 'cyan' :
                            ret.status === 'rejected' ? 'red' : 'default'
                        }>
                            {ret.status}
                        </Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="Причина">
                        {REASON_LABELS[ret.reason_type] || ret.reason_type}
                    </Descriptions.Item>
                    <Descriptions.Item label="Сумма возврата" span={2}>
                        <Text strong style={{ fontSize: 20, color: '#1890ff' }}>
                            {Number(ret.total_amount).toFixed(2)} ₽
                        </Text>
                    </Descriptions.Item>
                    {ret.description && (
                        <Descriptions.Item label="Комментарий" span={2}>
                            {ret.description}
                        </Descriptions.Item>
                    )}
                    {ret.rejection_reason && (
                        <Descriptions.Item label="Причина отклонения" span={2}>
                            <Text type="danger">{ret.rejection_reason}</Text>
                        </Descriptions.Item>
                    )}
                </Descriptions>
            </Card>

            <Divider />
            <Title level={4}>Товары ({ret.items.length})</Title>

            <List
                dataSource={ret.items}
                renderItem={item => (
                    <List.Item>
                        <List.Item.Meta
                            avatar={
                                <Image
                                    src={item.image_url || 'https://via.placeholder.com/80'}
                                    width={80} height={100}
                                    style={{ objectFit: 'cover' }}
                                    preview={false}
                                />
                            }
                            title={item.product_name || `Вариант #${item.variant_id}`}
                            description={
                                <Space direction="vertical" size={0}>
                                    <Text>{item.color_name} • {item.size_label}</Text>
                                    <Text>Количество: {item.quantity} шт.</Text>
                                </Space>
                            }
                        />
                        <Text strong style={{ fontSize: 18, color: '#1890ff' }}>
                            {Number(item.refund_amount).toFixed(2)} ₽
                        </Text>
                    </List.Item>
                )}
            />
        </div>
    );
}

export default ReturnDetailPage;