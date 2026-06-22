from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator


class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    overview: str | None = None
    overview_tr: str | None = None
    genres: str | None = None
    poster_url: str | None = None
    release_year: int | None = None
    content_type: str | None = None
    runtime: int | None = None
    letterboxd_rating: float | None = None
    positive_pct: float | None = None

    @field_validator("positive_pct", mode="before")
    @classmethod
    def clamp_positive_pct(cls, v):
        if v is None:
            return v
        return min(float(v), 100.0)


class WatchlistItemRead(MovieRead):
    added_at: datetime


class WatchHistoryItemRead(MovieRead):
    watched_at: datetime


class MovieDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    overview: str | None = None
    overview_tr: str | None = None
    genres: str | None = None
    themes: str | None = None
    poster_url: str | None = None
    release_year: int | None = None
    actors: str | None = None
    director: str | None = None
    tagline: str | None = None
    tagline_tr: str | None = None
    runtime: int | None = None
    letterboxd_rating: float | None = None
    audience_score: float | None = None
    tomato_meter: float | None = None
    total_reviews: int | None = None
    positive_pct: float | None = None
    content_type: str | None = None

    @field_validator("positive_pct", mode="before")
    @classmethod
    def clamp_positive_pct(cls, v):
        if v is None:
            return v
        return min(float(v), 100.0)



class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_text: str
    sentiment: str | None = None
    critic_name: str | None = None
