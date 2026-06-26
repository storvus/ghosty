import { Badge, Layout, List, Space, Typography } from 'antd'

import { presenceBadge } from 'src/utils/presence'

import styles from './ContactsList.module.css'
import { Chat } from 'src/services/api'

const { Sider } = Layout

const { Text } = Typography

interface ContactsListProps {
  chats: Chat[],
  activeUid: number | null
  // unreadMessagesCount: Record<string, number>
  onDialogOpen: (conversation_id: number) => void
}

export const ContactsList = ({
  chats,
  activeUid,
  onDialogOpen,
}: ContactsListProps) => (
  <Sider width={220} theme="light" className={styles.sider}>
    <div className={styles.siderHeading}>Contacts</div>
    <List
      dataSource={chats}
      locale={{
        emptyText: <Text type="secondary" className={styles.contactPresence}>No contacts online</Text>,
      }}
      renderItem={(sub) => (
        <List.Item
          className={`${styles.contactItem}${activeUid === sub.conversation_id ? ` ${styles.contactItemActive}` : ''}`}
          onClick={() => onDialogOpen(sub.conversation_id)}
        >
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Space size={8}>
              <Badge status={presenceBadge('hui')} />
              <div>
                <Text className={styles.contactName}>{sub.conversation_id}</Text>
                {/*<Text type="secondary" className={styles.contactPresence}>{sub.presence}</Text>*/}
              </div>
            </Space>
            <Badge count={sub.unread_count ?? 0} size="small" />
          </Space>
        </List.Item>
      )}
    />
  </Sider>
)
