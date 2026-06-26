import type { ConnectionState } from 'src/types/events.ts'

export const STATUS_COLOR: Record<ConnectionState, string> = {
  CONNECTED:    'success',
  READY:        'success',
  INITIALIZING: 'processing',
  CONNECTING:   'processing',
  DISCONNECTED: 'error',
  AUTH_ERROR:   'error',
}

export const STATUS_BADGE: Record<ConnectionState, 'success' | 'processing' | 'error'> = {
  CONNECTED:    'success',
  READY:        'success',
  INITIALIZING: 'processing',
  CONNECTING:   'processing',
  DISCONNECTED: 'error',
  AUTH_ERROR:   'error',
}
