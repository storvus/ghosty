import jwt
from fastapi import HTTPException, status

from src.core.config import settings
from src.dto.current_user import CurrentUser
from src.dto.token_payload import TokenPayload
from src.repositories.user import UserRepository


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(self, token: str) -> CurrentUser:
        payload = self.decode_token(token)

        user = await self.user_repo.get_user_by_id(payload.user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return CurrentUser(
            id=user.id,
            username=user.username,
        )

    @staticmethod
    def decode_token(token: str) -> TokenPayload:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.TOKEN_ENCODE_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
