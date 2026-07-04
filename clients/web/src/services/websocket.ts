import type { OutgoingEvent, IncomingEvent, ConnectionStateEvent } from '../types/events'

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000'

type MessageHandler = (event: IncomingEvent) => void
type ConnectionStateHandler = (event: ConnectionStateEvent) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private messageHandlers = new Set<MessageHandler>()
  private connectionStateHandlers = new Set<ConnectionStateHandler>()
  // connected only
  private connected = false

  // connected and initialized
  private initialized = false
  private buffer = new Array<IncomingEvent>()

  connect() {
    if (this.ws) return

    const token = localStorage.getItem('access_token')
    if (!token) return

    this.emit({ status: 'CONNECTING' })

    const ws = new WebSocket(`${WS_URL}/ws?token=${encodeURIComponent(token)}`)
    this.ws = ws

    // Each handler captures `ws` locally and bails out if a newer connection
    // has already taken over (guards against React StrictMode's double-invoke).
    ws.onopen = () => {
      if (this.ws !== ws) return
      this.emit({ status: 'CONNECTED' })
    }

    ws.onmessage = (ev: MessageEvent<string>) => {
      if (this.ws !== ws) return
      let data
      try {
        data = JSON.parse(ev.data) as IncomingEvent
      } catch { return }

      if (data.type === 'connected') {
        this.connected = true
        this.buffer.push(data)
        this.emit({ status: 'INITIALIZING', user: data.user })
        return
      }

      if (!this.connected) return

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
        this.emit({ status: 'AUTH_ERROR' })
      } else {
        this.emit({ status: 'DISCONNECTED' })
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
    this.emit({ status: 'READY' })
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

  private emit(event: ConnectionStateEvent) {
    this.connectionStateHandlers.forEach((h) => h(event))
  }
}

export const wsService = new WebSocketService()
