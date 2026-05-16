import type { Subscription, Exception } from '../types/events'

const API_URL = 'http://localhost:8000'

export async function getUid(): Promise<string> {
  const res = await fetch(`${API_URL}/uid`)
  if (!res.ok) throw new Error('Failed to get UID')
  const data = await res.json()
  return data.uid as string
}

export async function getSubscriptions(uid: string): Promise<Subscription[]> {
  const res = await fetch(`${API_URL}/subscriptions?uid=${encodeURIComponent(uid)}`)
  if (!res.ok) throw new Error('Failed to fetch subscriptions')
  return res.json() as Promise<Subscription[]>
}

export async function getExceptions(uid: string): Promise<Exception[]> {
  const res = await fetch(`${API_URL}/exceptions?uid=${encodeURIComponent(uid)}`)
  if (!res.ok) throw new Error('Failed to fetch exceptions')
  return res.json() as Promise<Exception[]>
}
