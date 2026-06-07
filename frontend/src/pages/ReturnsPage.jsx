// frontend/src/pages/ReturnsPage.jsx
import React, { useEffect, useState } from 'react';
import { returnService } from '../services/returnService';
import {
  Typography, Table, Tag, Button, Space, Empty, Spin, Popconfirm, message
} from 'antd';
import {
  RotateLeftOutlined, EyeOutlined, CloseCircleOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const STATUS_CONFIG = {
  pending:   { color: 'blue',    text: 'Ожидает рассмотрения' },
  approved:  { color: 'green',   text: 'Одобрено' },
  rejected:  { color: 'red',     text: 'Отклонено' },
  refunded:  { color: 'cyan',    text: 'Средства возвращены' },
  cancelled: { color: 'default', text: 'Отменено' },
  failed:    { color: 'volcano', text: 'Ошибка возврата' },
};

function ReturnsPage() {
  const [returns, setReturns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const fetchReturns = async () => {
    try {
      const res = await returnService.getReturns();
      setReturns(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (e) {
      message.error('Не удалось загрузить возвраты');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReturns(); }, []);

  const handleCancel = async (returnId) => {
    try {
      await returnService.cancelReturn(returnId);
      message.success('Заявка отменена');
      fetchReturns();
    } catch (e) {
      message.error(e.response?.data?.detail || 'Ошибка отмены');
    }
  };

  const columns = [
    {
      title: '№',
      dataIndex: 'id',
      key: 'id',
      render: (id) => `#${id.substring(0, 8)}`
    },
    {
      title: 'Дата',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (d) => new Date(d).toLocaleDateString('ru-RU')
    },
    {
      title: 'Сумма',
      dataIndex: 'refund_amount', // ИСПРАВЛЕНО: заменено с total_amount на refund_amount
      key: 'refund_amount',
      render: (v) => `${Number(v).toFixed(2)} ₽`
    },
    {
      title: 'Статус',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const cfg = STATUS_CONFIG[status] || { color: 'default', text: status };
        return <Tag color={cfg.color}>{cfg.text}</Tag>;
      }
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            size="small"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/returns/${record.id}`)}
          >
            Детали
          </Button>
          {record.status === 'pending' && (
            <Popconfirm
              title="Отменить заявку?"
              onConfirm={() => handleCancel(record.id)}
            >
              <Button
                size="small"
                danger
                icon={<CloseCircleOutlined />}
              >
                Отменить
              </Button>
            </Popconfirm>
          )}
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={2}>
        <RotateLeftOutlined style={{ marginRight: 12 }} />
        Мои возвраты
      </Title>
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <Spin size="large" />
        </div>
      ) : returns.length === 0 ? (
        <Empty description="У вас пока нет возвратов" />
      ) : (
        <Table
          dataSource={returns}
          columns={columns}
          rowKey="id"
          pagination={{ total, pageSize: 10 }}
        />
      )}
    </div>
  );
}

export default ReturnsPage;