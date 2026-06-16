import type { OutgoingEvent, IncomingEvent, ConnectionStatus } from '../types/events'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

type MessageHandler = (event: IncomingEvent) => void
type StatusHandler = (status: ConnectionStatus) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private messageHandlers = new Set<MessageHandler>()
  private statusHandlers = new Set<StatusHandler>()

  connect() {
    if (this.ws) return

    const token = localStorage.getItem('access_token')
    if (!token) return

    this.emit('CONNECTING')

    const ws = new WebSocket(`${WS_URL}/ws?token=${encodeURIComponent(token)}`)
    this.ws = ws

    // Each handler captures `ws` locally and bails out if a newer connection
    // has already taken over (guards against React StrictMode's double-invoke).
    ws.onopen = () => {
      if (this.ws !== ws) return
      this.emit('CONNECTED')
      this.send({ type: 'hello', presence: 'online' })
    }

    ws.onmessage = (ev: MessageEvent<string>) => {
      if (this.ws !== ws) return
      try {
        const data = JSON.parse(ev.data) as IncomingEvent
        this.messageHandlers.forEach((h) => h(data))
      } catch {
        // ignore malformed frames
      }
    }

    ws.onclose = (ev: CloseEvent) => {
      if (this.ws !== ws) return
      this.ws = null
      // Code 4001 means the server explicitly rejected the token (expired / invalid)
      if (ev.code === 4001) {
        this.emit('AUTH_ERROR')
      } else {
        this.emit('DISCONNECTED')
      }
    }

    ws.onerror = () => {
      if (this.ws !== ws) return
      ws.close()
    }
  }

  disconnect() {
    const ws = this.ws
    this.ws = null  // clear first so stale onclose is ignored
    ws?.close()
  }

  send(event: OutgoingEvent) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(event))
    }
  }

  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler)
    return () => this.messageHandlers.delete(handler)
  }

  onStatus(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler)
    return () => this.statusHandlers.delete(handler)
  }

  private emit(status: ConnectionStatus) {
    this.statusHandlers.forEach((h) => h(status))
  }
}

export const wsService = new WebSocketService()
