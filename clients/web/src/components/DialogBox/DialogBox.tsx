import { Typography } from 'antd'
import { ChatEntry } from 'src/types/events'

import styles from 'src/components/DialogBox/DialogBox.module.css'
import { useEffect, useRef } from 'react'

const { Text } = Typography

interface DialogProps {
  activeChatId: number | null
  dialogs: Record<number, ChatEntry[]>
}

export const DialogBox = ({
  activeChatId,
  dialogs,
}: DialogProps) => {
  const activeEntries = activeChatId != null ? (dialogs[activeChatId] ?? []) : []
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [activeEntries.length, activeChatId])

  return (
    <>
      {!activeChatId && (
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
                <Text strong className={entry.sender === 'me' ? styles.senderSelf : styles.senderOther}>
                  {entry.sender}:&nbsp;
                </Text>
                <Text className={styles.entryText}>{entry.text}</Text>
              </>
            ) : (
              <Text type="secondary" italic className={styles.entryText}>
                * {entry.text}
              </Text>
            )}
            <Text type="secondary" className={styles.entryTime}>
              {entry.ts.toLocaleTimeString()}
            </Text>
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </>
  )
}
