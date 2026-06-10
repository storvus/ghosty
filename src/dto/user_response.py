from pydantic import BaseModel

from src.models import User


class UserResponse(BaseModel):
    id: int
    username: str
    display_number: int

    @classmethod
    def from_user(cls, user: User):
        return cls(
            id=user.id,
            username=user.username,
            display_number=user.display_number,
        )
