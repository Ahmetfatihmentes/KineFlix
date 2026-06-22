import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.deps import get_current_user_id
from backend.core.database import get_db
from backend.models.movie import Movie
from backend.models.watch_history import WatchHistory
from backend.services.recommender import movie_recommender


router = APIRouter()


def _movie_payload(movie: Movie) -> dict:
    return {
        "id": movie.id,
        "title": movie.title,
        "overview": movie.overview_tr or movie.overview,
        "genres": movie.genres,
        "poster_url": movie.poster_url,
        "release_year": movie.release_year,
        "letterboxd_rating": movie.letterboxd_rating,
        "content_type": movie.content_type,
    }


async def _get_high_rated_random(db: AsyncSession) -> dict | None:
    result = await db.execute(
        select(Movie)
        .where(Movie.letterboxd_rating >= 4.0)
        .order_by(func.random())
        .limit(1)
    )
    random_movie = result.scalar_one_or_none()
    if not random_movie:
        return None

    return {
        "type": "general",
        "source_movie_id": None,
        "source_movie_title": None,
        "recommended_movie": _movie_payload(random_movie),
    }


@router.get("/personalized")
async def get_personalized_recommendation(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Kullanıcının son izlediği filme göre kişisel öneri döndürür.
    Watch history boşsa yüksek puanlı rastgele film döndürür.
    """
    result = await db.execute(
        select(WatchHistory)
        .where(WatchHistory.user_id == user_id)
        .order_by(WatchHistory.watched_at.desc())
        .limit(5)
    )
    last_watched_list = list(result.scalars().all())

    if last_watched_list and movie_recommender.is_ready:
        source_entry = random.choice(last_watched_list)
        candidates = movie_recommender.recommend(source_entry.movie_id, top_k=10)
        if candidates:
            recommended_id = candidates[0].movie_id
            result2 = await db.execute(select(Movie).where(Movie.id == recommended_id))
            recommended = result2.scalar_one_or_none()

            result3 = await db.execute(select(Movie).where(Movie.id == source_entry.movie_id))
            source = result3.scalar_one_or_none()

            if recommended and source:
                return {
                    "type": "personalized",
                    "source_movie_id": source.id,
                    "source_movie_title": source.title,
                    "recommended_movie": _movie_payload(recommended),
                }

    general = await _get_high_rated_random(db)
    if general:
        return general

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Öneri bulunamadı")
