from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    username: str
    display_number: int

    @classmethod
    def from_dict(cls, user: dict) -> UserInfo:
        return cls(
            id=user["id"],
            username=user["username"],
            display_number=user["display_number"],
        )
