// Outgoing events (client → server)

import { User } from 'src/types/users'

export interface HelloEvent {
  type: 'hello'
  presence: 'online' | 'away' | 'offline'
}

export interface MessageEvent {
  type: 'message'
  conversation_id: number | null
  recipient_id: number | null
  client_message_id: string
  message: string
}

export type UserPresence = 'online' | 'away' | 'do_not_disturb'

export interface PresenceUpdateEvent {
  type: 'presence'
  presence: UserPresence
}

export type OutgoingEvent = HelloEvent | MessageEvent | PresenceUpdateEvent

// Incoming events (server → client)
// Note: the server does not include a `type` field on chat/presence events.

// export interface IncomingChatMessage {
//   type: 'incoming_message'
//   from_uid: string
//   from_username: string
//   message: string
// }

export interface ConnectionEstablished {
  type: 'connected'
  user: User
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

// export interface IncomingNotifyPresence {
//   type: 'notify_presence'
//   subject_user_id: string
//   presence: string
// }

export type IncomingEvent = ConnectionEstablished

// UI model

export type ConnectionStateEvent =
  | { status: 'CONNECTING' }
  | { status: 'CONNECTED' }
  | { status: 'INITIALIZING'; user: User }
  | { status: 'READY' }
  | { status: 'DISCONNECTED' }
  | { status: 'AUTH_ERROR' }


export interface Subscription {
  uid: string
  name: string
  presence: string
}


