import { useState } from 'react'
import { Badge, Button, Layout, List, Space, Typography } from 'antd'

import { presenceBadge } from 'src/utils/presence'
import { UserSearch } from 'src/components/UserSearch/UserSearch'

import styles from './ContactsList.module.css'
import { User } from 'src/types/users'
import { Chat } from 'src/types/chats'

const { Sider } = Layout
const { Text } = Typography

interface ContactsListProps {
  chats: Chat[]
  activeChatId: string | null
  token: string
  onDialogOpen: (conversationId: string) => void
  onMessage: (user: User) => void
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
            className={`${styles.contactItem}${activeChatId === chat.conversationId ? ` ${styles.contactItemActive}` : ''}`}
            onClick={() => onDialogOpen(chat.conversationId)}
          >
            <Space style={{ width: '100%', justifyContent: 'space-between' }}>
              <Space size={8}>
                <Badge status={presenceBadge('offline')} />
                <div>
                  <Text className={styles.contactName}>{chat.title}</Text>
                  {chat.lastMessage && (
                    <Text type="secondary" className={styles.contactPresence}>
                      {chat.lastMessage.text.slice(0, 28)}
                      {chat.lastMessage.text.length > 28 ? '…' : ''}
                    </Text>
                  )}
                </div>
              </Space>
              <Badge count={chat.unreadCount ?? 0} size="small" />
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
