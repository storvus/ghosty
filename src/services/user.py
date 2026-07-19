import logging

import bcrypt
from fastapi import HTTPException, status

from src.dto.current_user import CurrentUser
from src.dto.login_request import LoginRequest
from src.dto.register_request import RegisterRequest
from src.dto.search_request import SearchRequest
from src.dto.token_response import TokenResponse
from src.dto.user_response import UserResponse
from src.models import User
from src.repositories.user import UserRepository
from src.utils import create_token, hash_password

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_session, user_repo: UserRepository):
        self.db_session = db_session
        self.user_repo = user_repo

    async def search(self, request: SearchRequest, current_user: CurrentUser) -> list[UserResponse]:
        users = await self.user_repo.search_users(request.username)
        # ToDo: filter out users who has banned the current_user?
        # exclude current user from the results
        return [UserResponse.from_user(user) for user in users if user.id != current_user.id]

    async def login(self, request: LoginRequest):
        user = await self.user_repo.get_by_username(request.username)
        if not user or not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )
        return TokenResponse(access_token=create_token(user.id))

    async def register(self, request: RegisterRequest) -> TokenResponse:
        user = await self.user_repo.get_by_username(request.username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        password_hash = hash_password(request.password)
        user = User.create(request.username, password_hash)
        self.user_repo.add(user)
        await self.db_session.commit()

        return TokenResponse(access_token=create_token(user.id))
