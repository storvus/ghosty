import { useState, useEffect, useCallback } from 'react'
import {
  Layout, Typography, Badge, Space, Spin, Grid, Tag,
} from 'antd'
import { wsService } from './services/websocket'
import {
  MessageEvent, ConnectionStateEvent,
} from './types/events'
import styles from './App.module.css'
import { ContactsList } from 'src/components/ContactsList/ContactsList'
// import { STATUS_BADGE, STATUS_COLOR } from 'src/constants.ts'
import { AuthModal } from 'src/components/AuthModal/AuthModal'
import { DialogBox } from 'src/components/DialogBox/DialogBox'
import { getChats } from 'src/services/api'
import { User } from 'src/types/users'
import { Chat, ChatId, ChatState, ChatType, LastMessage, Message } from 'src/types/chats'
import { generateNewMessageEvent } from 'src/utils/chats'

const { Header } = Layout
const { Text } = Typography

export default function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'))
  const [username, setUsername] = useState<string | null>(() => localStorage.getItem('username'))

  const [userCache, setUserCache] = useState<Record<number, User>>({})

  const [connectionState, setConnectionState] = useState<ConnectionStateEvent>({status: 'DISCONNECTED'})
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)
  const [myChats, setChats] = useState<Chat[]>([])

  const [dialogs, setDialogs] = useState<Record<ChatId, ChatState>>({})
  const [activeChatId, setActiveChatId] = useState<ChatId | null>(null)

  const screens = Grid.useBreakpoint()
  const isMobile = !screens.md

  const isNotConnected = connectionState.status !== 'READY'

  const handleLogout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
    setToken(null)
    setUsername(null)
    setChats([])
    setDialogs({})
    setActiveChatId(null)
  }, [])

  const openDialog = (chatId: string) => {
    setActiveChatId(chatId)
  }

  const handleMessage = (user: User) => {
    setUserCache((prev) => ({ ...prev, [user.id]: user }))
    const existingChat = myChats
      .find(c =>
        c.type === 'direct' &&
        c.participants.includes(user)
      )

    if (existingChat) {
      openDialog(existingChat.conversationId)
    } else {
      openDialog(`pending:${user.id}`)
    }
  }

  const handleLogin = useCallback((newToken: string, newUsername: string) => {
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('username', newUsername)
    setToken(newToken)
    setUsername(newUsername)
  }, [])

  const handleConnectionStateChange = useCallback(async (newConnectionState: ConnectionStateEvent) => {
    if (!token) return
    setConnectionState(newConnectionState)
    if (newConnectionState.status === 'AUTH_ERROR') {
      handleLogout()
      return
    }
    if (newConnectionState.status === 'INITIALIZING') {
      try {
        const chats = await getChats(token)
        setChats(chats)
        setCurrentUser(newConnectionState.user)

        const chatUsers: Record<number, User> = chats
          .flatMap(chat => chat.participants)
          .reduce((acc, user) => ({...acc, [user.id]: user}), {})
        setUserCache(prev => ({ ...prev, ...chatUsers }))

        setLoading(false)
      } finally {
        wsService.markInitialized()
      }
      return
    }
  }, [token, handleLogout])

  const addToDialog = useCallback((chatId: ChatId, message: Message) => {
    setDialogs((prev) => ({
      ...prev,
      [chatId]: {
        confirmed: prev[chatId]?.confirmed || [],
        pending: [
          ...(prev[chatId]?.pending || []),
          message,
        ],
      }
    }))
  }, [])
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
    addToDialog,
    handleConnectionStateChange,
  ])

  const handleSend = (messageText: string) => {
    const message = messageText.trim()
    if (!message || !activeChatId || isNotConnected || !currentUser) return
    const [chatPrefix, chatId] = activeChatId.split(':')

    const existingChat = myChats.find(c => c.conversationId === activeChatId)

    const clientMessageId = crypto.randomUUID()
    const lastMessage: LastMessage = {
      id: null,
      text: message,
      senderId: currentUser.id,
      createdAt: new Date().toISOString(),
      clientMessageId: clientMessageId,
    }
    const newMessageEvent = generateNewMessageEvent(chatId, clientMessageId, message, chatPrefix === 'pending')
    switch (chatPrefix) {
      case 'pending':
        const recipientId = parseInt(chatId, 10)
        if (!existingChat) {
          const newPendingChat = {
            type: 'direct' as ChatType,
            participants: [userCache[recipientId], currentUser],
            conversationId: activeChatId,
            lastMessage: lastMessage,
            unreadCount: 0,
            // ToDo: shouldn't be the case
            title: userCache[recipientId].username ?? 'Unknown user',
            oldestLoadedId: null
          }
          setChats((prev) => ([...prev, newPendingChat]))
        } else {
          existingChat.lastMessage = lastMessage
        }
        break
      case 'chat':
        if (!existingChat) {
          console.error(`No existing chat found for activeChatId: ${activeChatId}`)
          return
        }
        existingChat.lastMessage = lastMessage
        break
      default:
        console.error(`Unknown chat prefix: ${chatPrefix}`)
        return
    }
    wsService.send(newMessageEvent)

    const dialogMessage: Message = {
      id: null,
      clientMessageId: clientMessageId,
      kind: 'message',
      text: lastMessage.text,
      senderId: lastMessage.senderId,
      createdAt: lastMessage.createdAt,
      status: 'sending',
    }
    addToDialog(activeChatId, dialogMessage)
  }

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
            {/*{*/}
            {/*  isMobile*/}
            {/*    ? <Badge status={STATUS_BADGE[connectionState]} title={connectionState} />*/}
                : <Tag>{connectionState.status}</Tag>
            {/*}*/}
          </Space>
        </Header>

        {/* Middle row: chat + sider */}
        <Layout className={styles.overflowHidden}>

          {/* Chat column */}
          <DialogBox
            currentUser={currentUser}
            usersCache={userCache}
            dialog={activeChatId ? dialogs[activeChatId] : null}
            onSend={handleSend}
            disabled={isNotConnected || activeChatId === null}
          />

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
