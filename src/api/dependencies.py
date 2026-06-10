from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_session
from src.dto.current_user import CurrentUser

from src.dto.token_payload import TokenPayload
# from src.repositories.message import SqlAlchemyMessageRepository, MessageRepository
from src.repositories.user import SqlAlchemyUserRepository, UserRepository
from src.services.auth import AuthService
# from src.services.message import MessageService
# from src.services.presence import PresenceService
from src.services.user import UserService
from src.state import AppState, main_app_state


def get_app_state():
    return main_app_state

# repos
# def get_message_repo(
#     db: Annotated[AsyncSession, Depends(get_session)],
# ) -> SqlAlchemyMessageRepository:
#     return SqlAlchemyMessageRepository(db)


def get_user_repo(db: Annotated[AsyncSession, Depends(get_session)]) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(db)


# services
def get_user_service(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserService:
    return UserService(db, user_repo)

def get_auth_service(user_repo: Annotated[UserRepository, Depends(get_user_repo)]) -> AuthService:
    return AuthService(user_repo)


# def get_message_service(
#     db: Annotated[AsyncSession, Depends(get_session)],
#     message_repo: Annotated[MessageRepository, Depends(get_message_repo)],
#     user_repo: Annotated[UserRepository, Depends(get_user_repo)],
# ) -> MessageService:
#     return MessageService(db, message_repo, user_repo)
#
#
# def get_presence_service(
#     app_state: Annotated[AppState, Depends(get_app_state)],
# ) -> PresenceService:
#     return PresenceService(app_state)


security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> CurrentUser:
    return auth_service.authenticate(credentials.credentials)
