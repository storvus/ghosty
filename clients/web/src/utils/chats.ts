import { MessageEvent } from 'src/types/events'
import { ChatId } from 'src/types/chats'

export const generateNewMessageEvent = (
  chatId: ChatId,
  clientMessageId: string,
  message: string,
  isPending: boolean
): MessageEvent => {
  const chatNumberId = parseInt(chatId, 10)
  return {
    type: "message",
    conversation_id: isPending ? null : chatNumberId,
    recipient_id: isPending ? chatNumberId : null,
    client_message_id: clientMessageId,
    message,
  }
}
