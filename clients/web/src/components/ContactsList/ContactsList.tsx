import { useState } from 'react'
import { Badge, Button, Layout, List, Space, Typography } from 'antd'

import { presenceBadge } from 'src/utils/presence'
import { UserSearch } from 'src/components/UserSearch/UserSearch'
import { Chat, UserResult } from 'src/services/api'

import styles from './ContactsList.module.css'

const { Sider } = Layout
const { Text } = Typography

interface ContactsListProps {
  chats: Chat[]
  activeChatId: number | null
  token: string
  onDialogOpen: (conversation_id: number) => void
  onMessage: (user: UserResult) => void
}

export const ContactsList = ({
  chats,
  activeChatId,
  token,
  onDialogOpen,
  onMessage,
}: ContactsListProps) => {
  const [searchOpen, setSearchOpen] = useState(false)

  return (
    <Sider width={280} theme="light" className={styles.sider}>
      <div className={styles.siderHeading}>Contacts</div>

      <List
        dataSource={chats}
        locale={{
          emptyText: <Text type="secondary" className={styles.contactPresence}>No contacts yet</Text>,
        }}
        renderItem={(chat) => (
          <List.Item
            className={`${styles.contactItem}${activeChatId === chat.conversation_id ? ` ${styles.contactItemActive}` : ''}`}
            onClick={() => onDialogOpen(chat.conversation_id)}
          >
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space size={8}>
                <Badge status={presenceBadge('offline')} />
                <div>
                  <Text className={styles.contactName}>Chat #{chat.conversation_id}</Text>
                  {chat.last_message[0] && (
                    <Text type="secondary" className={styles.contactPresence}>
                      {chat.last_message[0].text.slice(0, 28)}
                      {chat.last_message[0].text.length > 28 ? '…' : ''}
                    </Text>
                  )}
                </div>
              </Space>
              <Badge count={chat.unread_count ?? 0} size="small" />
            </Space>
          </List.Item>
        )}
      />

      <div className={styles.findUsersRow}>
        <Button
          type="dashed"
          block
          onClick={() => setSearchOpen(true)}
          className={styles.findUsersBtn}
        >
          Find / Add Users
        </Button>
      </div>

      <UserSearch
        open={searchOpen}
        token={token}
        onClose={() => setSearchOpen(false)}
        onMessage={onMessage}
      />
    </Sider>
  )
}
