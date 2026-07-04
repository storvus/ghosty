import { User } from 'src/types/users'
import { Chat, ChatResponse } from 'src/types/chats'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export class UnauthorizedError extends Error {
  constructor() { super('Session expired. Please log in again.') }
}

export interface AuthResult {
  access_token: string
  token_type: string
}

export async function login(username: string, password: string): Promise<AuthResult> {
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? 'Login failed')
  }
  return res.json()
}

export async function register(username: string, password: string): Promise<AuthResult> {
  const res = await fetch(`${API_URL}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? 'Registration failed')
  }
  return res.json()
}

export async function getChats(token: string): Promise<Chat[]> {
  const res = await fetch(`${API_URL}/chats`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` },
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? 'Failed to get chats list')
  }
  const chats = await res.json()
  return chats.map((chat: ChatResponse) => ({
    type: chat.type,
    participants: chat.participants,
    conversationId: `chat:${chat.conversation_id}`,
    lastMessage: chat.last_message && {
      id: chat.last_message.id,
      text: chat.last_message.text,
      senderId: chat.last_message.sender_id,
      createdAt: chat.last_message.created_at,
    },
    unreadCount: chat.unread_count,
    title: chat.title,
    oldestLoadedId: chat.last_message?.id ?? null,
  }))
}

export async function searchUsers(token: string, username: string): Promise<User[]> {
  const res = await fetch(`${API_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ username }),
  })
  if (res.status === 401) throw new UnauthorizedError()
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? 'Search failed')
  }
  return res.json()
}
