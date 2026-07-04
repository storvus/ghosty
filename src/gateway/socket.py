import logging
from typing import Annotated

from fastapi import APIRouter, WebSocket, Depends, HTTPException
from starlette.websockets import WebSocketDisconnect

from src.api.dependencies import get_app_state, get_connection_manager, get_auth_service
from src.constants import ConnectionState
from src.dataclass import ClientSession
from src.managers.connection import ConnectionManager
from src.services.auth import AuthService
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
    # user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    # message_service: Annotated[MessageService, Depends(get_message_service)],
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

    # ToDo: to move into ConnectionManager one day
    await ws.send_json({"type": "connected", "user": current_user.to_dict()})

    peer_session = ClientSession(ws=ws, user_id=1, state=ConnectionState.AUTHENTICATED)
    app_state.add_connection(peer_session)

    try:
        while True:
            raw_data = await ws.receive_json()
            # try:
            #     event = parse_event(raw_data)
            # except ValidationError as e:
            #     logger.warning("Failed to parse event: %s", e)
            #     # ToDo: Outbound message
            #     await connection_manager.send(
            #         user_id, {"type": "error", "message": "invalid payload"}
            #     )
            #     continue
            #
            # response_events = await dispatch_event(
            #     message_service,
            #     presence_service,
            #     event,
            #     peer_session,
            #     app_state,
            # )
            # for r in response_events:
            #     await connection_manager.send(r)
    except WebSocketDisconnect:
        logger.info("User disconnected")
    # finally:
    #     await handle_disconnect(presence_service, peer_session, app_state)
