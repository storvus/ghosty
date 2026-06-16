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
