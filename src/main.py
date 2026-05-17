import asyncio
import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from starlette.websockets import WebSocketDisconnect

from src.aliases import UserId
from src.constants import ConnectionState
from src.dataclass import ClientSession
from src.events import HelloEvent
from src.handlers import dispatch_event, handle_disconnect
from src.managers.connection import ConnectionManager
from src.parser import parse_event
from src.state import AppState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app_state = AppState()
connection_manager = ConnectionManager(app_state)


@app.get("/api/uid")
async def create_uid():
    return {"uid": str(uuid4())}


@app.get("/api/exceptions")
async def get_exceptions(uid: str):  # noqa: ARG001
    return []


@app.get("/api/subscriptions")
async def get_subscriptions(uid: str):
    return [
        {"uid": user_id, "name": user_id, "presence": presence.value}
        for user_id, presence in app_state.presence_by_user.items()
        if user_id != uid
    ]


def is_token_valid(token: str) -> tuple[bool, UserId]:
    return bool(token), token


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    logger.info(f"New WS connection attempt, {id(ws)}")
    valid, user_id = is_token_valid(ws.headers.get("token") or ws.query_params.get("token"))
    if not valid:
        raise HTTPException(status_code=401)

    await ws.accept()
    peer_session = ClientSession(ws=ws, user_id=user_id, state=ConnectionState.AUTHENTICATED)

    try:
        raw_data = await asyncio.wait_for(ws.receive_json(), timeout=5)
    except asyncio.TimeoutError:
        logger.info("Client did not send hello within timeout, closing connection")
        await ws.close(code=1008)
        return
    except WebSocketDisconnect:
        logger.info("Client disconnected before hello")
        return

    try:
        event = parse_event(raw_data)
    except ValidationError as e:
        logger.warning("Failed to parse event: %s", e)
        await ws.close(code=1008)
        return

    if not isinstance(event, HelloEvent):
        logger.error("First event must be a 'hello', received: %s", event)
        await ws.close(code=1003)
        return

    await dispatch_event(event, peer_session, app_state)
    try:
        while True:
            raw_data = await ws.receive_json()
            try:
                event = parse_event(raw_data)
            except ValidationError as e:
                logger.warning("Failed to parse event: %s", e)
                # ToDo: Outbound message
                await connection_manager.send(user_id, {"type": "error", "message": "invalid payload"})
                continue

            response_events = await dispatch_event(event, peer_session, app_state)
            for r in response_events:
                await connection_manager.send(r)

    except WebSocketDisconnect:
        logger.info("User disconnected")
    finally:
        await handle_disconnect(peer_session, app_state)
