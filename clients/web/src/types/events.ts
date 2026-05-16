// Outgoing events (client → server)

export interface HelloEvent {
  type: 'hello'
  presence: 'online' | 'away' | 'offline'
}

export interface SendMessageEvent {
  type: 'message'
  recipient_id: string
  message: string
}

export type UserPresence = 'online' | 'away' | 'do_not_disturb'

export interface PresenceUpdateEvent {
  type: 'presence'
  presence: UserPresence
}

export type OutgoingEvent = HelloEvent | SendMessageEvent | PresenceUpdateEvent

// Incoming events (server → client)
// Note: the server does not include a `type` field on chat/presence events.

export interface IncomingChatMessage {
  from: string
  message: string
}

export interface IncomingPresenceEvent {
  user_id: string
  presence: string
}

export interface IncomingPresenceUpdated {
  type: 'presence_updated'
  presence: string
}

export interface IncomingNotifyPresence {
  type: 'notify_presence'
  subject_user_id: string
  presence: string
}

export type IncomingEvent = IncomingChatMessage | IncomingPresenceEvent | IncomingPresenceUpdated | IncomingNotifyPresence | Record<string, unknown>

// UI model

export type ConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED'

export interface Subscription {
  uid: string
  name: string
  presence: string
}

// Stub — will be expanded when the backend supports it
export interface Exception {
  uid: string
}

export interface ChatEntry {
  id: string
  kind: 'message' | 'system'
  sender?: string
  text: string
  ts: Date
}
