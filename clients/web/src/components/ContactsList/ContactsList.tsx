import { Badge, Layout, List, Space, Typography } from 'antd'

import { presenceBadge } from 'src/utils/presence'

import styles from './ContactsList.module.css'

const { Sider } = Layout

const { Text } = Typography

export interface Subscription {
  uid: string
  name: string
  presence: string
}

interface ContactsListProps {
  subscriptions: Subscription[],
  activeUid: string | null
  unreadMessagesCount: Record<string, number>
  onDialogOpen: (uid: string) => void
}

export const ContactsList = ({
  subscriptions,
  activeUid,
  unreadMessagesCount,
  onDialogOpen,
}: ContactsListProps) => (
  <Sider width={220} theme="light" className={styles.sider}>
    <div className={styles.siderHeading}>Contacts</div>
    <List
      dataSource={subscriptions}
      locale={{
        emptyText: <Text type="secondary" className={styles.contactPresence}>No contacts online</Text>,
      }}
      renderItem={(sub) => (
        <List.Item
          className={`${styles.contactItem}${activeUid === sub.uid ? ` ${styles.contactItemActive}` : ''}`}
          onClick={() => onDialogOpen(sub.uid)}
        >
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Space size={8}>
              <Badge status={presenceBadge(sub.presence)} />
              <div>
                <Text className={styles.contactName}>{sub.name}</Text>
                <Text type="secondary" className={styles.contactPresence}>{sub.presence}</Text>
              </div>
            </Space>
            <Badge count={unreadMessagesCount[sub.uid] ?? 0} size="small" />
          </Space>
        </List.Item>
      )}
    />
  </Sider>
)
