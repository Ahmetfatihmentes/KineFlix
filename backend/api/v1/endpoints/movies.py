from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.models.movie import Movie
from backend.models.review import Review
from backend.schemas.movie import MovieDetailRead, MovieRead, ReviewRead
from backend.services import movie_service
from backend.services.ollama_service import generate_recommendation_reason, generate_review_summary
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


@router.get("/{movie_id}/recommendation-reason")
async def get_recommendation_reason(
    movie_id: int,
    recommended_id: int,
    short: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """İki film arasındaki benzerlik açıklaması döndürür."""
    result1 = await db.execute(select(Movie).where(Movie.id == movie_id))
    source = result1.scalar_one_or_none()

    result2 = await db.execute(select(Movie).where(Movie.id == recommended_id))
    recommended = result2.scalar_one_or_none()

    if not source or not recommended:
        raise HTTPException(status_code=404, detail="Film bulunamadı")

    reason = await generate_recommendation_reason(
        source_movie_title=source.title,
        source_movie_genres=source.genres or "",
        source_movie_overview=source.overview or "",
        source_movie_overview_tr=source.overview_tr or "",
        source_movie_director=source.director or "",
        source_movie_actors=source.actors or "",
        source_movie_themes=source.themes or "",
        source_movie_score=source.audience_score,
        recommended_movie_title=recommended.title,
        recommended_movie_genres=recommended.genres or "",
        recommended_movie_overview=recommended.overview or "",
        recommended_movie_overview_tr=recommended.overview_tr or "",
        recommended_movie_director=recommended.director or "",
        recommended_movie_actors=recommended.actors or "",
        recommended_movie_themes=recommended.themes or "",
        recommended_movie_score=recommended.audience_score,
        source_content_type=source.content_type or "Movie",
        recommended_content_type=recommended.content_type or "Movie",
        short_mode=short,
    )

    return {
        "source_movie": source.title,
        "recommended_movie": recommended.title,
        "reason": reason or "Bu filmler benzer türde ve temaya sahip yapımlar.",
    }


@router.get("/{movie_id}/ai-review")
async def get_ai_review(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Film için AI tarafından üretilmiş Türkçe genel değerlendirme döndürür."""
    result = await db.execute(select(Movie).where(Movie.id == movie_id))
    movie = result.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Film bulunamadı")

    reviews_result = await db.execute(
        select(Review.review_text)
        .where(Review.movie_id == movie_id)
        .limit(8)
    )
    review_texts = [r[0] for r in reviews_result.fetchall() if r[0]]

    if not review_texts:
        return {
            "movie_id": movie_id,
            "movie_title": movie.title,
            "ai_review": None,
            "review_count": 0,
            "has_reviews": False,
        }

    summary = await generate_review_summary(
        movie_title=movie.title,
        reviews=review_texts,
        positive_pct=movie.positive_pct,
    )

    return {
        "movie_id": movie_id,
        "movie_title": movie.title,
        "ai_review": summary,
        "review_count": len(review_texts),
        "has_reviews": True,
    }


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
