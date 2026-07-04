import { User } from 'src/types/users'

export interface LastMessageResponse {
  id: number | null
  text: string
  sender_id: number
  created_at: string
}

export interface LastMessage {
  id: number | null
  text: string
  senderId: number
  createdAt: string
  clientMessageId?: string
}

export type ChatId = string
export type ChatType = 'direct' | 'group'

export interface ChatResponse {
  type: ChatType
  participants: User[],
  conversation_id: number
  last_message: LastMessageResponse | null
  unread_count: number
  title: string
}

export interface Chat {
  type: ChatType
  participants: User[],
  conversationId: string
  lastMessage: LastMessage | null
  unreadCount: number
  title: string
  oldestLoadedId: number | null
}

interface OutgoingMessage {
  id: number | null
  clientMessageId: string
  kind: 'message'
  text: string
  senderId: number
  createdAt: string
  status: 'sending' | 'confirmed' | 'error'
}

interface IncomingMessage {
  id: number
  clientMessageId: null
  kind: 'message' | 'service'
  text: string
  senderId: number // ToDo: an object or a number?
  createdAt: string
  status: null
}

export type Message = OutgoingMessage | IncomingMessage

export interface ChatState {
  confirmed: Message[]
  pending: Message[]
  // failed: Message[]
}
