from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.models.movie import Movie
from backend.schemas.movie import MovieDetailRead, MovieRead, ReviewRead
from backend.services import movie_service
from backend.services.tmdb_trailer import fetch_trailer_key


router = APIRouter()


@router.get("/search", response_model=list[MovieRead])
async def search_movies(
    q: str = Query("", alias="query"),
    content_type: str | None = Query(None, description="Movie veya TV Show"),
    db: AsyncSession = Depends(get_db),
) -> list[MovieRead]:
    """
    Search movies by title or overview.
    """
    return await movie_service.search_movies(db=db, query=q, content_type=content_type)


@router.get("/{movie_id}", response_model=MovieDetailRead)
async def get_movie(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> MovieDetailRead:
    """
    Get movie details by id.
    """
    movie = await movie_service.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return movie_service.to_movie_detail_read(movie)


@router.get("/{movie_id}/reviews", response_model=list[ReviewRead])
async def get_movie_reviews(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[ReviewRead]:
    """
    Get reviews for a given movie id.
    """
    reviews = await movie_service.get_reviews_for_movie(
        db=db, movie_id=movie_id, limit=limit
    )
    if reviews is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return reviews


@router.get("/{movie_id}/trailer")
async def get_movie_trailer(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Film bulunamadı",
        )

    if movie.trailer_key:
        return {
            "youtube_key": movie.trailer_key,
            "youtube_url": f"https://www.youtube.com/watch?v={movie.trailer_key}",
            "cached": True,
        }

    settings = get_settings()
    if not settings.TMDB_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TMDB API anahtarı yapılandırılmamış",
        )

    trailer_key = await fetch_trailer_key(movie, settings.TMDB_API_KEY)
    if not trailer_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bu film için fragman bulunamadı",
        )

    movie.trailer_key = trailer_key
    await db.commit()

    return {
        "youtube_key": trailer_key,
        "youtube_url": f"https://www.youtube.com/watch?v={trailer_key}",
        "cached": False,
    }
