from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.movie import MovieRead
from backend.services import movie_service
from backend.services.recommender import movie_recommender


router = APIRouter()


@router.get("/{movie_id}/recommendations")
async def get_recommendations(
    movie_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recommended movies for a given movie id.
    """
    if not movie_recommender.is_ready:
        if not movie_recommender.is_loading:
            await movie_recommender.start_background_initialization()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "loading",
                "message": "Model hazırlanıyor, lütfen bekleyin",
            },
        )

    recommendations = await movie_service.get_recommendations_for_movie(
        db=db, movie_id=movie_id, limit=limit
    )
    if recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )
    return [MovieRead.model_validate(movie) for movie in recommendations]
