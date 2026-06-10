import type { ConnectionStatus } from 'src/types/events.ts'

export const STATUS_COLOR: Record<ConnectionStatus, string> = {
  CONNECTED: 'success',
  CONNECTING: 'processing',
  DISCONNECTED: 'error',
}

export const STATUS_BADGE: Record<ConnectionStatus, 'success' | 'processing' | 'error'> = {
  CONNECTED:    'success',
  CONNECTING:   'processing',
  DISCONNECTED: 'error',
}
