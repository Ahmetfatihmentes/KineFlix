from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


class MovieRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    overview: str | None = None
    genres: str | None = None
    poster_url: str | None = None
    release_year: int | None = None
    content_type: str | None = None


class MovieDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    overview: str | None = None
    genres: str | None = None
    themes: str | None = None
    poster_url: str | None = None
    release_year: int | None = None
    actors: str | None = None
    director: str | None = None
    tagline: str | None = None
    runtime: int | None = None
    letterboxd_rating: float | None = None
    audience_score: float | None = None
    tomato_meter: float | None = None
    total_reviews: int | None = None
    positive_pct: float | None = None
    content_type: str | None = None

    @model_validator(mode="after")
    def normalize_tv_rating(self) -> Self:
        if self.content_type == "TV Show" and self.letterboxd_rating is not None:
            self.letterboxd_rating = round(self.letterboxd_rating / 2, 1)
        return self


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_text: str
    sentiment: str | None = None
    critic_name: str | None = None
