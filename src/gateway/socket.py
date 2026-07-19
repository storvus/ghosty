import logging
from typing import Annotated

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.api.dependencies import get_app_state, get_connection_manager, get_auth_service, get_message_service
from src.constants import ConnectionState
from src.dataclass import ClientSession
from src.dto.outgoing_envelope import OutgoingEnvelope
from src.gateway.dispatcher import dispatch_event
from src.managers.connection import ConnectionManager
from src.parser import parse_event
from src.payloads._user_info import UserInfo
from src.payloads.connected import SessionConnectedPayload
from src.services.auth import AuthService
from src.services.message import MessageService
from src.state import AppState

# from src.api.dependencies import (
#     get_message_service,
#     get_presence_service,
# )
# from src.gateway.dispatcher import dispatch_event

logger = logging.getLogger(__name__)

HELLO_EVENT_TIMEOUT_SEC = 5

router = APIRouter(tags=["Configurations"])
#
#
# async def is_token_valid(
#     user_repo: UserRepository, token: str | None
# ) -> tuple[bool, UserId]:
#     if not token:
#         return False, -1
#
#     # ToDo: get username from token
#     username = token
#     user_id = await user_repo.get_or_create_user(username)
#     return bool(token), user_id


@router.websocket("/ws")
async def ws_endpoint(
    ws: WebSocket,
    app_state: Annotated[AppState, Depends(get_app_state)],
    connection_manager: Annotated[ConnectionManager, Depends(get_connection_manager)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    message_service: Annotated[MessageService, Depends(get_message_service)],
    # presence_service: Annotated[PresenceService, Depends(get_presence_service)],
):
    logger.info(f"New WS connection attempt, {id(ws)}")
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=4001)
        return

    try:
        current_user = await auth_service.authenticate(token)
    except HTTPException:
        await ws.close(code=4001)
        return

    await ws.accept()

    peer_session = ClientSession(
        ws=ws,
        user_id=current_user.id,
        state=ConnectionState.AUTHENTICATED
    )
    app_state.add_connection(peer_session)

    envelope_connected = OutgoingEnvelope(
        payload=SessionConnectedPayload(
            user=UserInfo.from_dict(current_user.to_dict()),
        ),
        user_ids=[current_user.id]
    )
    await connection_manager.send_to_session(envelope_connected, peer_session)

    try:
        while True:
            raw_data = await ws.receive_json()
            try:
                event = parse_event(raw_data)
            except ValidationError as e:
                logger.warning("Failed to parse event: %s", e)
                # ToDo: Outbound message
                # await connection_manager.send(
                #     user_id, {"type": "error", "message": "invalid payload"}
                # )
                continue

            envelopes = await dispatch_event(current_user, message_service, event)
            for e in envelopes:
                if e.type == "message_ack":
                    await connection_manager.send_to_session(e, peer_session)
                elif e.type == "new_message":
                    await connection_manager.send(e, exclude_connection_ids=[peer_session.connection_id])

    except WebSocketDisconnect:
        logger.info("User disconnected")
    # finally:
    #     await handle_disconnect(presence_service, peer_session, app_state)
