from pydantic import BaseModel

from src.payloads._user_info import UserInfo


class SessionConnectedPayload(BaseModel):
    type: str = "connected"
    user: UserInfo
