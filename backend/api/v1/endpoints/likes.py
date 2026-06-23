from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.models.movie_like import MovieLike

router = APIRouter()


@router.post("/{movie_id}", status_code=201)
async def toggle_like(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    result = await db.execute(
        select(MovieLike).where(
            MovieLike.user_id == user_id,
            MovieLike.movie_id == movie_id,
        )
    )
    like = result.scalar_one_or_none()

    if like:
        await db.delete(like)
        await db.commit()
        return {"liked": False}

    db.add(MovieLike(user_id=user_id, movie_id=movie_id))
    await db.commit()
    return {"liked": True}


@router.get("/{movie_id}/status")
async def get_like_status(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    result = await db.execute(
        select(MovieLike).where(
            MovieLike.user_id == user_id,
            MovieLike.movie_id == movie_id,
        )
    )
    like = result.scalar_one_or_none()

    count_result = await db.execute(
        select(func.count()).select_from(MovieLike).where(MovieLike.movie_id == movie_id)
    )
    count = count_result.scalar()

    return {"liked": like is not None, "like_count": count}
