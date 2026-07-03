import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Layout, Typography, Input, Button,
  Badge, Space, Spin, Grid, Tag,
} from 'antd'
import { wsService } from './services/websocket'
import type {
  ConnectionState,
  ChatEntry,
  Subscription,
} from './types/events'
import styles from './App.module.css'
import { ContactsList } from 'src/components/ContactsList/ContactsList'
import { STATUS_BADGE, STATUS_COLOR } from 'src/constants.ts'
import { AuthModal } from 'src/components/AuthModal/AuthModal'
import { DialogBox } from 'src/components/DialogBox/DialogBox'
import { Chat, UserResult, getChats } from 'src/services/api'

const { Content, Header, Footer } = Layout
const { Text } = Typography

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'))
  const [username, setUsername] = useState<string | null>(() => localStorage.getItem('username'))

  const [connectionState, setConnectionState] = useState<ConnectionState>('DISCONNECTED')
  // const [myPresence, setMyPresence] = useState<UserPresence>('online')
  const [_subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [loading, setLoading] = useState(false)
  const [myChats, setChats] = useState<Chat[]>([])

  const [dialogs, setDialogs] = useState<Record<number, ChatEntry[]>>({})
  const [activeChatId, setActiveChatId] = useState<number | null>(null)
  const [_unread, setUnread] = useState<Record<number, number>>({})

  const [messageText, setMessageText] = useState('')

  const activeChatIdRef = useRef<number | null>(null)
  const screens = Grid.useBreakpoint()
  const isMobile = !screens.md

  useEffect(() => { activeChatIdRef.current = activeChatId }, [activeChatId])

  const openDialog = (peerUid: number) => {
    setActiveChatId(peerUid)
    setUnread((prev) => ({ ...prev, [peerUid]: 0 }))
  }

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    setToken(null)
    setUsername(null)
    setChats([])
    setDialogs({})
    setUnread({})
    setActiveChatId(null)
  }, [])

  const handleMessage = useCallback((user: UserResult) => {
    setActiveChatId(user.id)
  }, [])

  const handleLogin = useCallback((newToken: string, newUsername: string) => {
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('username', newUsername)
    setToken(newToken)
    setUsername(newUsername)
  }, [])

  const handleConnectionStateChange = useCallback(async (newConnectionState: ConnectionState) => {
    if (!token) return
    setConnectionState(newConnectionState)
    if (newConnectionState === 'AUTH_ERROR') {
      handleLogout()
      return
    }
    if (newConnectionState === 'INITIALIZING') {
      try {
        const chats = await getChats(token)
        setChats(chats)
        setLoading(false)
      } finally {
        wsService.markInitialized()
      }
      return
    }
  }, [token, handleLogout])

  // const addToDialog = useCallback((peerUid: string, entry: Omit<ChatEntry, 'id' | 'ts'>) => {
  //   setDialogs((prev) => ({
  //     ...prev,
  //     [peerUid]: [
  //       ...(prev[peerUid] ?? []),
  //       { ...entry, id: crypto.randomUUID(), ts: new Date() },
  //     ],
  //   }))
  // }, [])
  //
  // const handleNotifyPresence = useCallback((event: IncomingNotifyPresence) => {
  //   setSubscriptions((prev) =>
  //     prev.map((s) => s.uid === event.subject_user_id ? { ...s, presence: event.presence } : s)
  //   )
  // }, [])
  //
  // const handleChatMessage = useCallback((event: IncomingChatMessage) => {
  //   const chatEntry = {
  //     kind: 'message',
  //     sender: event.from_username,
  //     text: event.message,
  //   } as ChatEntry
  //   addToDialog(event.from_uid, chatEntry)
  //
  //   if (activeChatId !== event.from_uid) {
  //     setUnread((prev) => ({ ...prev, [event.from_uid]: (prev[event.from_uid] ?? 0) + 1 }))
  //   }
  // }, [activeChatId, addToDialog])

  useEffect(() => {
    if (!token) return
    setLoading(true)
    const unsubscribeConnectionState = wsService.subscribeToConnectionState(handleConnectionStateChange)

    // const unsubscribeMessage = wsService.onMessage((event: IncomingEvent) => {
    //   switch (event.type) {
    //     case 'notify_presence':
    //       handleNotifyPresence(event)
    //       break
    //     case 'incoming_message':
    //       handleChatMessage(event)
    //       break
    //   }
    // })
    wsService.connect()
    return () => {
      unsubscribeConnectionState();
      // unsubscribeMessage();
      wsService.disconnect()
    }
  }, [
    token,
    // addToDialog,
    handleConnectionStateChange,
  ])

  // const handlePresenceChange = (value: UserPresence) => {
  //   setMyPresence(value)
  //   wsService.send({ type: 'presence', presence: value })
  // }
  //
  const handleSend = () => {
    const text = messageText.trim()
    if (!text || !activeChatId || connectionState !== 'CONNECTED') return
    wsService.send({ type: 'message', recipient_id: activeChatId, message: text })
    addToDialog(activeChatId, { kind: 'message', sender: 'me', text })
    setMessageText('')
  }
  //
  // const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
  //   if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  // }

  // const presenceOptions = [
  //   { value: 'online',         label: <><Badge status="success" /> Online</> },
  //   { value: 'away',           label: <><Badge status="warning" /> Away</> },
  //   { value: 'do_not_disturb', label: <><Badge status="error" />   Do not disturb</> },
  // ]

  // const contactsOptions = subscriptions.map((sub) => ({
  //   value: sub.uid,
  //   label: (
  //     <Space size={4}>
  //       <Badge status={presenceBadge(sub.presence)} />
  //       <span>{sub.name}</span>
  //       {(unread[sub.uid] ?? 0) > 0 && <Badge count={unread[sub.uid]} size="small" />}
  //     </Space>
  //   ),
  // }))

  return (
    <>
      {/* ── Loading overlay ───────────────────────────────── */}
      {loading && (
        <div className={styles.loadingOverlay}>
          <Spin size="large" />
        </div>
      )}

      <AuthModal open={!token} onLogin={handleLogin} />

      {/* ── Main layout ───────────────────────────────────── */}
      <Layout className={styles.appLayout}>
        <Header className={styles.header}>
          <span className={styles.logo}>ghosty</span>

          <Space size="middle">
            {username && <Text type="secondary" className={styles.uid}>{username}</Text>}

            {/* Mobile: contact picker lives in the header */}
            {/*{isMobile && (*/}
            {/*  <Select*/}
            {/*    size="small"*/}
            {/*    placeholder="Contact"*/}
            {/*    value={activeChatId ?? undefined}*/}
            {/*    onChange={openDialog}*/}
            {/*    className={styles.contactsSelect}*/}
            {/*    options={contactsOptions}*/}
            {/*  />*/}
            {/*)}*/}

            {/*<Select*/}
            {/*  size="small"*/}
            {/*  value={myPresence}*/}
            {/*  disabled={connectionState !== 'CONNECTED'}*/}
            {/*  onChange={handlePresenceChange}*/}
            {/*  className={styles.presenceSelect}*/}
            {/*  options={presenceOptions}*/}
            {/*/>*/}
            {
              isMobile
                ? <Badge status={STATUS_BADGE[connectionState]} title={connectionState} />
                : <Tag color={STATUS_COLOR[connectionState]}>{connectionState}</Tag>
            }
          </Space>
        </Header>

        {/* Middle row: chat + sider */}
        <Layout className={styles.overflowHidden}>

          {/* Chat column */}
          <Layout className={styles.overflowHidden}>
            <Content className={styles.messages}>
              <DialogBox dialogs={dialogs} activeChatId={activeChatId} />
            </Content>
            <Footer className={styles.compose}>

              <Input.TextArea
                placeholder={activeChatId ? 'Type a message… (Enter to send)' : 'Select a contact first'}
                rows={2}
                disabled={!activeChatId}
                value={messageText}
                onChange={(e) => setMessageText(e.target.value)}
                // onKeyDown={handleKeyDown}
                style={{ flex: 1, resize: 'none' }}
              />
              <Button
                type="primary"
                onClick={handleSend}
                disabled={!activeChatId || connectionState !== 'READY'}
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
                chats={myChats}
                activeChatId={activeChatId}
                token={token ?? ''}
                onDialogOpen={openDialog}
                onMessage={handleMessage}
              />
            )
          }

        </Layout>
      </Layout>
    </>
  )
}
