import { useState } from 'react'
import { Modal, Input, Button, List, Space, Typography, Spin } from 'antd'
import { UserResult, searchUsers } from 'src/services/api'
import styles from './UserSearch.module.css'

const { Text } = Typography

interface UserSearchProps {
  open: boolean
  token: string
  onClose: () => void
  onMessage: (user: UserResult) => void
}

export const UserSearch = ({ open, token, onClose, onMessage }: UserSearchProps) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<UserResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    const q = query.trim()
    if (!q) return
    setLoading(true)
    setError(null)
    setSearched(true)
    try {
      setResults(await searchUsers(token, q))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Search failed')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setQuery('')
    setResults([])
    setError(null)
    setSearched(false)
    onClose()
  }

  return (
    <Modal
      title="Find Users"
      open={open}
      onCancel={handleClose}
      footer={null}
      width={420}
    >
      <div className={styles.searchRow}>
        <Input
          placeholder="Enter username…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onPressEnter={handleSearch}
          allowClear
          autoFocus
        />
        <Button type="primary" onClick={handleSearch} loading={loading}>
          Search
        </Button>
      </div>

      {error && <Text type="danger" className={styles.feedback}>{error}</Text>}

      {loading && (
        <div className={styles.spinner}><Spin /></div>
      )}

      {!loading && searched && (
        <List
          dataSource={results}
          locale={{ emptyText: <Text type="secondary">No users found</Text> }}
          renderItem={(user) => (
            <List.Item
              className={styles.resultItem}
              actions={[
                <Button
                  size="small"
                  type="primary"
                  onClick={() => { onMessage(user); handleClose() }}
                >
                  Message
                </Button>,
              ]}
            >
              <Space direction="vertical" size={0}>
                <Text className={styles.resultName}>{user.username}</Text>
                <Text type="secondary" className={styles.resultUin}>#{user.display_number}</Text>
              </Space>
            </List.Item>
          )}
        />
      )}
    </Modal>
  )
}
