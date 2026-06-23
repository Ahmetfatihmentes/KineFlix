from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    overview_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    genres: Mapped[str | None] = mapped_column(String(255), nullable=True)
    themes: Mapped[str | None] = mapped_column(Text, nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actors: Mapped[str | None] = mapped_column(Text, nullable=True)
    director: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tagline: Mapped[str | None] = mapped_column(String(512), nullable=True)
    tagline_tr: Mapped[str | None] = mapped_column(String(512), nullable=True)
    runtime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    letterboxd_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    audience_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    tomato_meter: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_reviews: Mapped[int | None] = mapped_column(Integer, nullable=True)
    positive_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default="Movie")
    trailer_key: Mapped[str | None] = mapped_column(String(32), nullable=True)

    watch_history: Mapped[list["WatchHistory"]] = relationship(
        "WatchHistory", back_populates="movie", cascade="all, delete-orphan"
    )
    watchlist: Mapped[list["Watchlist"]] = relationship(
        "Watchlist", back_populates="movie", cascade="all, delete-orphan"
    )

