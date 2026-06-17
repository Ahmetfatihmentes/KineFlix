from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.movie import MovieDetailRead, MovieRead, ReviewRead
from backend.services import movie_service


router = APIRouter()


@router.get("/search", response_model=list[MovieRead])
async def search_movies(
    q: str = Query(..., alias="query", min_length=1),
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
