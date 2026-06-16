import { useState } from 'react'
import { Alert, Button, Form, Input, Modal, Tabs, Typography } from 'antd'
import { login, register } from 'src/services/api'

const { Title } = Typography

interface AuthModalProps {
  open: boolean
  onLogin: (token: string, username: string) => void
}

export const AuthModal = ({ open, onLogin }: AuthModalProps) => {
  const [tab, setTab] = useState<'login' | 'register'>('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form] = Form.useForm()

  const handleTabChange = (key: string) => {
    setTab(key as 'login' | 'register')
    setError(null)
    form.resetFields()
  }

  const handleFinish = async (values: { username: string; password: string }) => {
    setLoading(true)
    setError(null)
    try {
      const result = tab === 'login'
        ? await login(values.username, values.password)
        : await register(values.username, values.password)
      onLogin(result.access_token, values.username)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      open={open}
      closable={false}
      maskClosable={false}
      footer={null}
      centered
      title={<Title level={4} style={{ margin: 0 }}>Welcome to Ghosty</Title>}
    >
      <Tabs
        activeKey={tab}
        onChange={handleTabChange}
        items={[
          { key: 'login', label: 'Log in' },
          { key: 'register', label: 'Register' },
        ]}
      />

      {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 12 }} />}

      <Form form={form} layout="vertical" onFinish={handleFinish}>
        <Form.Item
          name="username"
          label="Username"
          rules={[
            { required: true, message: 'Please enter your username' },
            ...(tab === 'register' ? [{ min: 3, message: 'At least 3 characters' }] : []),
          ]}
        >
          <Input autoComplete="username" />
        </Form.Item>

        <Form.Item
          name="password"
          label="Password"
          rules={[
            { required: true, message: 'Please enter your password' },
            ...(tab === 'register' ? [{ min: 6, message: 'At least 6 characters' }] : []),
          ]}
        >
          <Input.Password
            autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0 }}>
          <Button type="primary" htmlType="submit" block size="large" loading={loading}>
            {tab === 'login' ? 'Log in' : 'Create account'}
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  )
}
