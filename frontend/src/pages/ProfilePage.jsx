import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { userService } from '../services/userService';
import { Descriptions, Button, Form, Input, message } from 'antd';

function ProfilePage() {
  const { user, setUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (user) {
      form.setFieldsValue(user);
    }
  }, [user, form]);

  const onFinish = async (values) => {
    try {
      const res = await userService.updateMe(values);
      setUser(res.data);
      message.success('Профиль обновлён');
      setEditing(false);
    } catch (e) {
      message.error('Ошибка обновления');
    }
  };

  if (!user) return null;

  return (
    <div>
      <h2>Личный кабинет</h2>
      {!editing ? (
        <>
          <Descriptions column={1}>
            <Descriptions.Item label="Имя">{user.first_name} {user.last_name}</Descriptions.Item>
            <Descriptions.Item label="Email">{user.email}</Descriptions.Item>
            <Descriptions.Item label="Телефон">{user.phone || '-'}</Descriptions.Item>
          </Descriptions>
          <Button type="primary" onClick={() => setEditing(true)}>Редактировать</Button>
        </>
      ) : (
        <Form form={form} onFinish={onFinish} layout="vertical" initialValues={user}>
          <Form.Item name="first_name" label="Имя">
            <Input />
          </Form.Item>
          <Form.Item name="last_name" label="Фамилия">
            <Input />
          </Form.Item>
          <Form.Item name="phone" label="Телефон">
            <Input />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">Сохранить</Button>
            <Button onClick={() => setEditing(false)} style={{ marginLeft: 8 }}>Отмена</Button>
          </Form.Item>
        </Form>
      )}
    </div>
  );
}

export default ProfilePage;