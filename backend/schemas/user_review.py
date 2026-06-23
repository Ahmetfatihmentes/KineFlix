from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserReviewCreate(BaseModel):
    movie_id: int
    review_text: str


class UserReviewRead(BaseModel):
    id: int
    user_id: int
    movie_id: int
    review_text: str
    sentiment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
