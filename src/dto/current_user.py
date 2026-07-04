from pydantic import BaseModel

from src.models import User


class CurrentUser(BaseModel):
    id: int
    username: str
    display_number: int

    @classmethod
    def from_user(cls, user: User) -> CurrentUser:
        return cls(
            id=user.id,
            username=user.username,
            display_number=user.display_number,
        )

    def to_dict(self):
        """Converts the object fields into standard JSON types."""
        return {
            "id": self.id,
            "username": self.username,
            "display_number": self.display_number,
        }
