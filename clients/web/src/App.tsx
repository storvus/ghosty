import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Layout, Typography, Tag, Input, Button, Modal,
  Divider, List, Badge, Space, Spin, Select, theme,
} from 'antd'
import { wsService } from './services/websocket'
import { getUid, getSubscriptions, getExceptions } from './services/api'
import type {
  ConnectionStatus,
  UserPresence,
  ChatEntry,
  IncomingEvent,
  IncomingChatMessage,
  IncomingNotifyPresence,
  Subscription,
} from './types/events'

const { Header, Content, Footer, Sider } = Layout
const { Text, Title } = Typography

function isChatMessage(e: IncomingEvent): e is IncomingChatMessage {
  return 'from' in e && 'message' in e
}

function isNotifyPresence(e: IncomingEvent): e is IncomingNotifyPresence {
  return (e as IncomingNotifyPresence).type === 'notify_presence'
}

const STATUS_COLOR: Record<ConnectionStatus, string> = {
  CONNECTED: 'success',
  CONNECTING: 'processing',
  DISCONNECTED: 'error',
}

function presenceBadge(presence: string): 'success' | 'warning' | 'error' | 'default' {
  switch (presence) {
    case 'online': return 'success'
    case 'away': return 'warning'
    case 'do_not_disturb': return 'error'
    default: return 'default'
  }
}

export default function App() {
  const [uid, setUid] = useState<string | null>(() => localStorage.getItem('uid'))
  const [manualUid, setManualUid] = useState('')
  const [gettingUid, setGettingUid] = useState(false)

  const [status, setStatus] = useState<ConnectionStatus>('DISCONNECTED')
  const [myPresence, setMyPresence] = useState<UserPresence>('online')
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [loading, setLoading] = useState(false)

  // Per-peer message history
  const [dialogs, setDialogs] = useState<Record<string, ChatEntry[]>>({})
  const [activeUid, setActiveUid] = useState<string | null>(null)
  const [unread, setUnread] = useState<Record<string, number>>({})

  const [messageText, setMessageText] = useState('')

  // Ref so the WS message handler can read activeUid without stale closure
  const activeUidRef = useRef<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const { token } = theme.useToken()

  useEffect(() => {
    activeUidRef.current = activeUid
  }, [activeUid])

  const resolveUid = (newUid: string) => {
    localStorage.setItem('uid', newUid)
    setUid(newUid)
  }

  const handleGetUid = async () => {
    setGettingUid(true)
    try {
      resolveUid(await getUid())
    } finally {
      setGettingUid(false)
    }
  }

  const handleUseManualUid = () => {
    const trimmed = manualUid.trim()
    if (trimmed) resolveUid(trimmed)
  }

  const openDialog = (peerUid: string) => {
    setActiveUid(peerUid)
    setUnread((prev) => ({ ...prev, [peerUid]: 0 }))
  }

  const addToDialog = useCallback((peerUid: string, entry: Omit<ChatEntry, 'id' | 'ts'>) => {
    setDialogs((prev) => ({
      ...prev,
      [peerUid]: [
        ...(prev[peerUid] ?? []),
        { ...entry, id: crypto.randomUUID(), ts: new Date() },
      ],
    }))
  }, [])

  useEffect(() => {
    if (!uid) return

    setLoading(true)
    Promise.all([getSubscriptions(uid), getExceptions(uid)])
      .then(([subs]) => setSubscriptions(subs))
      .catch(() => {})
      .finally(() => setLoading(false))

    const offStatus = wsService.onStatus(setStatus)
    const offMessage = wsService.onMessage((event: IncomingEvent) => {
      if (isChatMessage(event)) {
        addToDialog(event.from, { kind: 'message', sender: event.from, text: event.message })
        if (activeUidRef.current !== event.from) {
          setUnread((u) => ({ ...u, [event.from]: (u[event.from] ?? 0) + 1 }))
        }
      } else if (isNotifyPresence(event)) {
        setSubscriptions((prev) =>
          prev.map((s) =>
            s.uid === event.subject_user_id ? { ...s, presence: event.presence } : s
          )
        )
      }
    })
    wsService.connect()

    return () => {
      offStatus()
      offMessage()
      wsService.disconnect()
    }
  }, [uid, addToDialog])

  const activeEntries = activeUid != null ? (dialogs[activeUid] ?? []) : []

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeEntries.length, activeUid])

  const handlePresenceChange = (value: UserPresence) => {
    setMyPresence(value)
    wsService.send({ type: 'presence', presence: value })
  }

  const handleSend = () => {
    const text = messageText.trim()
    if (!text || !activeUid || status !== 'CONNECTED') return
    wsService.send({ type: 'message', recipient_id: activeUid, message: text })
    addToDialog(activeUid, { kind: 'message', sender: 'me', text })
    setMessageText('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      {/* ── Full-screen loading overlay ──────────────────── */}
      {loading && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9999,
            background: 'rgba(255, 255, 255, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Spin size="large" />
        </div>
      )}

      {/* ── UID setup modal ──────────────────────────────── */}
      <Modal
        open={!uid}
        closable={false}
        maskClosable={false}
        footer={null}
        centered
        title={<Title level={4} style={{ margin: 0 }}>Welcome to Ghosty</Title>}
      >
        <Space direction="vertical" style={{ width: '100%', marginTop: 8 }} size="middle">
          <Button
            type="primary"
            block
            size="large"
            loading={gettingUid}
            onClick={handleGetUid}
          >
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
            <Button onClick={handleUseManualUid} disabled={!manualUid.trim()}>
              Use it
            </Button>
          </Space.Compact>
        </Space>
      </Modal>

      {/* ── Main layout ──────────────────────────────────── */}
      <Layout style={{ height: '100%' }}>
        <Header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
            padding: '0 16px',
            height: 48,
            lineHeight: 'normal',
            flexShrink: 0,
          }}
        >
          <Text strong style={{ fontSize: 16, color: token.colorPrimary, letterSpacing: 3 }}>
            ghosty
          </Text>
          <Space size="middle">
            {uid && (
              <Text type="secondary" style={{ fontSize: 11 }}>{uid}</Text>
            )}
            <Select
              size="small"
              value={myPresence}
              disabled={status !== 'CONNECTED'}
              onChange={handlePresenceChange}
              style={{ width: 152 }}
              options={[
                { value: 'online',          label: <><Badge status="success" /> Online</> },
                { value: 'away',            label: <><Badge status="warning" /> Away</> },
                { value: 'do_not_disturb',  label: <><Badge status="error" />   Do not disturb</> },
              ]}
            />
            <Tag color={STATUS_COLOR[status]}>{status}</Tag>
          </Space>
        </Header>

        {/* Middle row: chat column + contacts sider */}
        <Layout style={{ overflow: 'hidden' }}>

          {/* Chat column */}
          <Layout style={{ overflow: 'hidden' }}>
            <Content
              style={{
                overflowY: 'auto',
                padding: '12px 16px',
                background: token.colorBgLayout,
                display: 'flex',
                flexDirection: 'column',
                gap: 6,
              }}
            >
              {!activeUid ? (
                <div style={{
                  flex: 1,
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Text type="secondary">Select a contact to start chatting</Text>
                </div>
              ) : activeEntries.length === 0 ? (
                <Text type="secondary" style={{ textAlign: 'center', marginTop: 48, display: 'block' }}>
                  No messages yet.
                </Text>
              ) : (
                activeEntries.map((entry) => (
                  <div
                    key={entry.id}
                    style={{ display: 'flex', alignItems: 'baseline', gap: 4, lineHeight: 1.6 }}
                  >
                    {entry.kind === 'message' ? (
                      <>
                        <Text
                          strong
                          style={{
                            color: entry.sender === 'me' ? token.colorSuccess : token.colorPrimary,
                            flexShrink: 0,
                          }}
                        >
                          {entry.sender}:&nbsp;
                        </Text>
                        <Text style={{ flex: 1, wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
                          {entry.text}
                        </Text>
                      </>
                    ) : (
                      <Text type="secondary" italic style={{ flex: 1 }}>
                        * {entry.text}
                      </Text>
                    )}
                    <Text type="secondary" style={{ fontSize: 11, flexShrink: 0, marginLeft: 8 }}>
                      {entry.ts.toLocaleTimeString()}
                    </Text>
                  </div>
                ))
              )}
              <div ref={bottomRef} />
            </Content>

            <Footer
              style={{
                background: token.colorBgContainer,
                borderTop: `1px solid ${token.colorBorderSecondary}`,
                padding: '10px 16px',
                display: 'flex',
                gap: 8,
                flexShrink: 0,
              }}
            >
              <Input.TextArea
                placeholder={activeUid ? 'Type a message… (Enter to send)' : 'Select a contact first'}
                rows={2}
                disabled={!activeUid}
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                onKeyDown={handleKeyDown}
                style={{ flex: 1, resize: 'none' }}
              />
              <Button
                type="primary"
                onClick={handleSend}
                disabled={!activeUid || status !== 'CONNECTED'}
                style={{ alignSelf: 'stretch', height: 'auto' }}
              >
                Send
              </Button>
            </Footer>
          </Layout>

          {/* Contacts sider */}
          <Sider
            width={220}
            theme="light"
            style={{
              borderLeft: `1px solid ${token.colorBorderSecondary}`,
              overflowY: 'auto',
            }}
          >
            <div
              style={{
                padding: '10px 14px 6px',
                borderBottom: `1px solid ${token.colorBorderSecondary}`,
              }}
            >
              <Text strong style={{ fontSize: 12, color: token.colorTextSecondary }}>
                CONTACTS
              </Text>
            </div>
            <List
              dataSource={subscriptions}
              locale={{
                emptyText: (
                  <Text type="secondary" style={{ fontSize: 12 }}>No contacts online</Text>
                ),
              }}
              renderItem={(sub) => (
                <List.Item
                  style={{
                    padding: '8px 14px',
                    cursor: 'pointer',
                    background: activeUid === sub.uid ? token.colorBgTextHover : 'transparent',
                  }}
                  onClick={() => openDialog(sub.uid)}
                >
                  <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                    <Space size={8}>
                      <Badge status={presenceBadge(sub.presence)} />
                      <div>
                        <Text style={{ fontSize: 13, display: 'block' }}>{sub.name}</Text>
                        <Text type="secondary" style={{ fontSize: 11 }}>{sub.presence}</Text>
                      </div>
                    </Space>
                    <Badge count={unread[sub.uid] ?? 0} size="small" />
                  </Space>
                </List.Item>
              )}
            />
          </Sider>

        </Layout>
      </Layout>
    </>
  )
}
