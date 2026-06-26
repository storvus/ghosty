import type { OutgoingEvent, IncomingEvent, ConnectionState } from '../types/events'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

type MessageHandler = (event: IncomingEvent) => void
type ConnectionStateHandler = (status: ConnectionState) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private messageHandlers = new Set<MessageHandler>()
  private connectionStateHandlers = new Set<ConnectionStateHandler>()
  private initialized = false
  private buffer = new Array<IncomingEvent>()

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
      // this.send({ type: 'hello', presence: 'online' })
    }

    ws.onmessage = (ev: MessageEvent<string>) => {
      if (this.ws !== ws) return
      let data
      try {
        data = JSON.parse(ev.data) as IncomingEvent
      } catch { return }

      if (data.type === 'connected') {
        this.emit('INITIALIZING')
        return
      }

      if (!this.initialized) {
        this.buffer.push(data)
        return
      }

      this.handleMessage(data)
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

  handleMessage(msg: IncomingEvent) {
    try {
      this.messageHandlers.forEach((h) => h(msg))
    } catch {
      // ignore malformed frames
    }
  }

  markInitialized() {
    this.initialized = true
    this.buffer.forEach(this.handleMessage)
    this.buffer = []
    this.emit('READY')
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

  subscribeToMessages(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler)
    return () => this.messageHandlers.delete(handler)
  }

  subscribeToConnectionState(handler: ConnectionStateHandler): () => void {
    this.connectionStateHandlers.add(handler)
    return () => this.connectionStateHandlers.delete(handler)
  }

  private emit(status: ConnectionState) {
    this.connectionStateHandlers.forEach((h) => h(status))
  }
}

export const wsService = new WebSocketService()
