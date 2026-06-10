from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str
