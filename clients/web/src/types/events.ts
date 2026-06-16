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
  type: 'incoming_message'
  from_uid: string
  from_username: string
  message: string
}

// export interface IncomingPresenceEvent {
//   type: 'incoming_message'
//   user_id: string
//   presence: string
// }

// export interface IncomingPresenceUpdated {
//   type: 'presence_updated'
//   presence: string
// }

export interface IncomingNotifyPresence {
  type: 'notify_presence'
  subject_user_id: string
  presence: string
}

export type IncomingEvent = IncomingChatMessage | IncomingNotifyPresence

// UI model

export type ConnectionStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'AUTH_ERROR'

export interface Subscription {
  uid: string
  name: string
  presence: string
}

export interface ChatEntry {
  id: string
  kind: 'message' | 'system'
  sender?: string
  text: string
  ts: Date
}
