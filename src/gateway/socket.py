# import asyncio
# import logging
# from typing import Annotated
#
# from fastapi import APIRouter, Depends, HTTPException, WebSocket
# from pydantic import ValidationError
# from starlette.websockets import WebSocketDisconnect
#
# from src.aliases import UserId
# from src.api.dependencies import (
#     get_app_state,
#     get_message_service,
#     get_presence_service,
#     get_user_repo,
# )
# from src.gateway.dispatcher import dispatch_event
# from src.constants import ConnectionState
# from src.dataclass import ClientSession
# from src.events import HelloEvent
# from src.handlers.presence import handle_disconnect
# from src.managers.connection import ConnectionManager
# from src.parser import parse_event
# from src.repositories.user import UserRepository
# from src.services.message import MessageService
# from src.services.presence import PresenceService
# from src.state import AppState
#
# logger = logging.getLogger(__name__)
#
# HELLO_EVENT_TIMEOUT_SEC = 5
#
# router = APIRouter(tags=["Configurations"])
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
#
#
# @router.websocket("/ws")
# async def ws_endpoint(
#     ws: WebSocket,
#     app_state: Annotated[AppState, Depends(get_app_state)],
#     user_repo: Annotated[UserRepository, Depends(get_user_repo)],
#     message_service: Annotated[MessageService, Depends(get_message_service)],
#     presence_service: Annotated[PresenceService, Depends(get_presence_service)],
# ):
#     logger.info(f"New WS connection attempt, {id(ws)}")
#     valid, user_id = await is_token_valid(user_repo, ws.query_params.get("token"))
#     if not valid:
#         raise HTTPException(status_code=401)
#
#     await ws.accept()
#     connection_manager = ConnectionManager(app_state)
#     peer_session = ClientSession(
#         ws=ws, user_id=user_id, state=ConnectionState.AUTHENTICATED
#     )
#
#     try:
#         raw_data = await asyncio.wait_for(
#             ws.receive_json(), timeout=HELLO_EVENT_TIMEOUT_SEC
#         )
#     except asyncio.TimeoutError:
#         logger.info("Client did not send hello within timeout, closing connection")
#         await ws.close(code=1008)
#         return
#     except WebSocketDisconnect:
#         logger.info("Client disconnected before hello")
#         return
#
#     try:
#         event = parse_event(raw_data)
#     except ValidationError as e:
#         logger.warning("Failed to parse event: %s", e)
#         await ws.close(code=1008)
#         return
#
#     if not isinstance(event, HelloEvent):
#         logger.error("First event must be a 'hello', received: %s", event)
#         await ws.close(code=1003)
#         return
#
#     await dispatch_event(
#         message_service, presence_service, event, peer_session, app_state
#     )
#     try:
#         while True:
#             raw_data = await ws.receive_json()
#             try:
#                 event = parse_event(raw_data)
#             except ValidationError as e:
#                 logger.warning("Failed to parse event: %s", e)
#                 # ToDo: Outbound message
#                 await connection_manager.send(
#                     user_id, {"type": "error", "message": "invalid payload"}
#                 )
#                 continue
#
#             response_events = await dispatch_event(
#                 message_service,
#                 presence_service,
#                 event,
#                 peer_session,
#                 app_state,
#             )
#             for r in response_events:
#                 await connection_manager.send(r)
#
#     except WebSocketDisconnect:
#         logger.info("User disconnected")
#     finally:
#         await handle_disconnect(presence_service, peer_session, app_state)
