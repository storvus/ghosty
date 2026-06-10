import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Layout, Typography, Input, Button,
  Badge, Space, Spin, Select, Grid, Tag,
} from 'antd'
import { wsService } from './services/websocket'
import { getSubscriptions, getExceptions } from './services/api'
import type {
  ConnectionStatus,
  UserPresence,
  ChatEntry,
  IncomingEvent,
  IncomingChatMessage,
  IncomingNotifyPresence,
  Subscription,
} from './types/events'
import styles from './App.module.css'
import { ContactsList } from 'src/components/ContactsList/ContactsList'
import { STATUS_BADGE, STATUS_COLOR } from 'src/constants.ts'
import { presenceBadge } from 'src/utils/presence.ts'
import { SignupModal } from 'src/components/SignupModal/SignupModal.tsx'
import { DialogBox } from 'src/components/DialogBox/DialogBox'

const { Content, Header, Footer } = Layout
const { Text } = Typography

export default function App() {
  const [uid, setUid] = useState<string | null>(() => localStorage.getItem('uid'))

  const [status, setStatus] = useState<ConnectionStatus>('DISCONNECTED')
  const [myPresence, setMyPresence] = useState<UserPresence>('online')
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [loading, setLoading] = useState(false)

  const [dialogs, setDialogs] = useState<Record<string, ChatEntry[]>>({})
  const [activeUid, setActiveUid] = useState<string | null>(null)
  const [unread, setUnread] = useState<Record<string, number>>({})

  const [messageText, setMessageText] = useState('')

  const activeUidRef = useRef<string | null>(null)
  const screens = Grid.useBreakpoint()
  const isMobile = !screens.md

  useEffect(() => { activeUidRef.current = activeUid }, [activeUid])

  const openDialog = (peerUid: string) => {
    setActiveUid(peerUid)
    setUnread((prev) => ({ ...prev, [peerUid]: 0 }))
  }

  const addToDialog = useCallback((peerUid: string, entry: Omit<ChatEntry, 'id' | 'ts'>) => {
    setDialogs((prev) => ({
      ...prev,
      [peerUid]: [
        ...(prev[peerUid] ?? []),
        // ToDo: Add clientId
        { ...entry, id: crypto.randomUUID(), ts: new Date() },
      ],
    }))
  }, [])

  const handleNotifyPresence = useCallback((event: IncomingNotifyPresence) => {
    setSubscriptions((prev) =>
      prev.map((s) => s.uid === event.subject_user_id ? { ...s, presence: event.presence } : s)
    )
  }, [])

  const handleChatMessage = useCallback((event: IncomingChatMessage) => {
    const chatEntry = {
      kind: 'message',
      sender: event.from_username,
      text: event.message,
    } as ChatEntry
    addToDialog(event.from_uid, chatEntry)

    if (activeUid !== event.from_uid) {
      // update the unread counter if a sender isn't active/focused
      setUnread((prev) => ({...prev, [event.from_uid]: (prev[event.from_uid] ?? 0) + 1}))
    }
  }, [activeUid, addToDialog])


  useEffect(() => {
    if (!uid) return

    setLoading(true)
    Promise.all([getSubscriptions(uid), getExceptions(uid)])
      .then(([subs]) => setSubscriptions(subs))
      .catch(() => {})
      .finally(() => setLoading(false))

    const unsubscribeStatus = wsService.onStatus(setStatus)

    const unsubscribeMessage = wsService.onMessage((event: IncomingEvent) => {
      switch (event.type) {
        case 'notify_presence':
          handleNotifyPresence(event)
          break

        case 'incoming_message':
          handleChatMessage(event)
          break
      }
    })

    wsService.connect()

    // on cleanup
    return () => { unsubscribeStatus(); unsubscribeMessage(); wsService.disconnect() }

  }, [uid, addToDialog])

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
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  const presenceOptions = [
    { value: 'online',         label: <><Badge status="success" /> Online</> },
    { value: 'away',           label: <><Badge status="warning" /> Away</> },
    { value: 'do_not_disturb', label: <><Badge status="error" />   Do not disturb</> },
  ]

  const contactsOptions = subscriptions.map((sub) => ({
    value: sub.uid,
    label: (
      <Space size={4}>
        <Badge status={presenceBadge(sub.presence)} />
        <span>{sub.name}</span>
        {(unread[sub.uid] ?? 0) > 0 && <Badge count={unread[sub.uid]} size="small" />}
      </Space>
    ),
  }))

  return (
    <>
      {/* ── Loading overlay ───────────────────────────────── */}
      {loading && (
        <div className={styles.loadingOverlay}>
          <Spin size="large" />
        </div>
      )}

      <SignupModal uid={uid} onSetUid={setUid}/>

      {/* ── Main layout ───────────────────────────────────── */}
      <Layout className={styles.appLayout}>
        <Header className={styles.header}>
          <span className={styles.logo}>ghosty</span>

          <Space size="middle">
            {uid && <Text type="secondary" className={styles.uid}>{uid}</Text>}

            {/* Mobile: contact picker lives in the header */}
            {isMobile && (
              <Select
                size="small"
                placeholder="Contact"
                value={activeUid ?? undefined}
                onChange={openDialog}
                className={styles.contactsSelect}
                options={contactsOptions}
              />
            )}

            <Select
              size="small"
              value={myPresence}
              disabled={status !== 'CONNECTED'}
              onChange={handlePresenceChange}
              className={styles.presenceSelect}
              options={presenceOptions}
            />
            {
              isMobile
                ? <Badge status={STATUS_BADGE[status]} title={status} />
                : <Tag color={STATUS_COLOR[status]}>{status}</Tag>
            }
          </Space>
        </Header>

        {/* Middle row: chat + sider */}
        <Layout className={styles.overflowHidden}>

          {/* Chat column */}
          <Layout className={styles.overflowHidden}>
            <Content className={styles.messages}>
              <DialogBox dialogs={dialogs} activeUid={activeUid} />
            </Content>
            <Footer className={styles.compose}>

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
                className={styles.sendBtn}
              >
                Send
              </Button>
            </Footer>
          </Layout>

          {/* Desktop: contacts sider */}
          {
            !isMobile && (
              <ContactsList
                subscriptions={subscriptions}
                activeUid={activeUid}
                unreadMessagesCount={unread}
                onDialogOpen={openDialog}
              />
            )
          }

        </Layout>
      </Layout>
    </>
  )
}
