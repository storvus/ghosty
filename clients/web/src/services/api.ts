const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export class UnauthorizedError extends Error {
  constructor() { super('Session expired. Please log in again.') }
}

export interface Message {
  id: number
  text: string
  sender_id: number
  created_at: string
}

export interface Chat {
  conversation_id: number
  last_message: Message[]
  unread_count: number
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
  return res.json()
}

export interface UserResult {
  id: number
  username: string
  display_number: number
}

export async function searchUsers(token: string, username: string): Promise<UserResult[]> {
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
