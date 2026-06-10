from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    username: str = Field(min_length=1)
