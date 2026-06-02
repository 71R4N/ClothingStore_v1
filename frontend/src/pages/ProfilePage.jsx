import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { userService } from '../services/userService';
import { Descriptions, Button, Form, Input, message, Typography } from 'antd';

const { Title } = Typography;

function ProfilePage() {
  const { user, setUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue(user);
    }
  }, [user, form]);

  const onFinish = async (values) => {
    setLoading(true);
    try {
      const res = await userService.updateProfile(values);
      setUser(res.data);
      message.success('Профиль обновлён');
      setEditing(false);
    } catch (e) {
      message.error(e.response?.data?.detail || 'Ошибка обновления');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <Title level={2}>Личный кабинет</Title>
      {!editing ? (
        <>
          <Descriptions column={1} bordered style={{ marginBottom: 24 }}>
            <Descriptions.Item label="Имя">{user.first_name} {user.last_name}</Descriptions.Item>
            <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
            <Descriptions.Item label="Телефон">{user.phone || '-'}</Descriptions.Item>
          </Descriptions>
          <Button type="primary" onClick={() => setEditing(true)}>Редактировать</Button>
        </>
      ) : (
        <Form form={form} onFinish={onFinish} layout="vertical" initialValues={user}>
          <Form.Item name="first_name" label="Имя" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="last_name" label="Фамилия" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Телефон">
            <Input placeholder="+79991234567" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>Сохранить</Button>
            <Button onClick={() => setEditing(false)} style={{ marginLeft: 8 }} disabled={loading}>Отмена</Button>
          </Form.Item>
        </Form>
      )}
    </div>
  );
}

export default ProfilePage;