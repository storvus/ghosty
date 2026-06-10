import { Button, Divider, Input, Modal, Space } from 'antd'
import { Typography } from 'antd'
import { useState } from 'react'
import { getUid } from 'src/services/api'

const { Title } = Typography

interface SignupModalProps {
  uid: string | null
  onSetUid: (uid: string) => void
}

export const SignupModal = ({
  uid,
  onSetUid,
}: SignupModalProps) => {

  const [manualUid, setManualUid] = useState('')
  const [gettingUid, setGettingUid] = useState(false)

  const resolveUid = (newUid: string) => {
    localStorage.setItem('uid', newUid)
    onSetUid(newUid)
  }

  const handleGetUid = async () => {
    setGettingUid(true)
    try { resolveUid(await getUid()) } finally { setGettingUid(false) }
  }

  const handleUseManualUid = () => {
    const trimmed = manualUid.trim()
    if (trimmed) resolveUid(trimmed)
  }

  return (
    <Modal
      open={!uid}
      closable={false}
      maskClosable={false}
      footer={null}
      centered
      title={<Title level={4} style={{ margin: 0 }}>Welcome to Ghosty</Title>}
    >
      <Space direction="vertical" style={{ width: '100%', marginTop: 8 }} size="middle">
        <Button type="primary" block size="large" loading={gettingUid} onClick={handleGetUid}>
          Get the UID
        </Button>

        <Divider plain style={{ margin: '4px 0' }}>or</Divider>

        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="I already have a UID"
            value={manualUid}
            onChange={(e) => setManualUid(e.target.value)}
            onPressEnter={handleUseManualUid}
          />
          <Button onClick={handleUseManualUid} disabled={!manualUid.trim()}>Use it</Button>
        </Space.Compact>
      </Space>
    </Modal>
  )
}
