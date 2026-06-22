from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_current_user, get_conversation_service
from src.dto.chat_response import ChatResponse
from src.dto.current_user import CurrentUser
from src.dto.message_response import MessageResponse
from src.services.conversation import ConversationService

router = APIRouter(tags=["User"])


@router.get("/chats/{chat_id}/history")
async def get_history(
    chat_id: int,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conversation_service: Annotated[ConversationService, Depends(get_conversation_service)],
    before_message_id: int = Query(),
) -> list[MessageResponse]:
    return await conversation_service.get_history(current_user, chat_id, before_message_id)


@router.get("/chats", response_model=list[ChatResponse],)
async def get_chats(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conversation_service: Annotated[ConversationService, Depends(get_conversation_service)],
):
    return await conversation_service.get_user_conversations(current_user)
