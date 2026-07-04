import { Button, Input, Layout, Typography } from 'antd'

import styles from 'src/components/DialogBox/DialogBox.module.css'
import { useEffect, useRef, useState } from 'react'
import { ChatState } from 'src/types/chats'
import { User } from 'src/types/users'

const { Content, Footer } = Layout
const { Text } = Typography

interface DialogProps {
  currentUser: User | null
  usersCache: Record<number, User>
  dialog: ChatState | null
  onSend: (message: string) => void
  disabled: boolean
}

export const DialogBox = ({
  currentUser,
  usersCache,
  dialog,
  onSend,
  disabled,
}: DialogProps) => {
  const [messageText, setMessageText] = useState('')
  const activeEntries = dialog ? [...dialog.confirmed, ...dialog.pending] : []
  const bottomRef = useRef<HTMLDivElement>(null)

  const handleSend = () => {
    if (messageText.trim() === '' || disabled) return
    onSend(messageText.trim())
    setMessageText('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeEntries.length, dialog])

  return (
    <Layout className={styles.overflowHidden}>
      <Content className={styles.messages}>
        {!dialog && (
          <div className={styles.emptyState}>
            <Text type="secondary">Select a contact to start chatting</Text>
          </div>
        )}
        {activeEntries.length === 0 && (
          <Text type="secondary" style={{ textAlign: 'center', marginTop: 48, display: 'block' }}>
            No messages yet.
          </Text>
        )}
        {activeEntries.length !== 0 && (
          activeEntries.map((entry) => (
            <div key={entry.id} className={styles.entry}>
              {entry.kind === 'message' ? (
                <>
                  <Text strong className={entry.senderId === currentUser?.id ? styles.senderSelf : styles.senderOther}>
                    {usersCache[entry.senderId].username}:&nbsp;
                  </Text>
                  <Text className={styles.entryText}>{entry.text}</Text>
                </>
              ) : (
                <Text type="secondary" italic className={styles.entryText}>
                  * {entry.text}
                </Text>
              )}
              <Text type="secondary" className={styles.entryTime}>
                {entry.createdAt}
              </Text>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </Content>
      <Footer className={styles.compose}>

        <Input.TextArea
          placeholder={!disabled ? 'Type a message… (Enter to send)' : 'Select a contact first'}
          rows={2}
          disabled={disabled}
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{ flex: 1, resize: 'none' }}
        />
        <Button
          type="primary"
          onClick={handleSend}
          disabled={disabled}
          className={styles.sendBtn}
        >
          Send
        </Button>
      </Footer>
    </Layout>
  )
}
