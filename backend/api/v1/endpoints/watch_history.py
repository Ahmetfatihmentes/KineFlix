from datetime import datetime, UTC

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.models.watch_history import WatchHistory
from backend.schemas.movie import MovieRead, WatchHistoryCreate, WatchHistoryItemRead


router = APIRouter()


@router.get("/", response_model=list[WatchHistoryItemRead])
async def list_watch_history(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[WatchHistoryItemRead]:
    statement = (
        select(WatchHistory)
        .where(WatchHistory.user_id == user_id)
        .options(selectinload(WatchHistory.movie))
        .order_by(WatchHistory.watched_at.desc())
        .limit(100)
    )
    result = await db.execute(statement)
    entries = result.scalars().all()
    items: list[WatchHistoryItemRead] = []
    for entry in entries:
        if entry.movie is None:
            continue
        movie_data = MovieRead.model_validate(entry.movie).model_dump()
        items.append(WatchHistoryItemRead(**movie_data, watched_at=entry.watched_at))
    return items


@router.get("/{movie_id}/status")
async def check_watch_status(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    result = await db.execute(
        select(WatchHistory).where(
            WatchHistory.user_id == user_id,
            WatchHistory.movie_id == movie_id,
        )
    )
    watched = result.scalar_one_or_none()
    return {"watched": watched is not None}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_watch_history(
    body: WatchHistoryCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    result = await db.execute(
        select(WatchHistory).where(
            WatchHistory.user_id == user_id,
            WatchHistory.movie_id == body.movie_id,
        )
    )
    if result.scalar_one_or_none():
        return {"message": "Zaten izlendi", "already_exists": True}

    entry = WatchHistory(
        user_id=user_id,
        movie_id=body.movie_id,
        watched_at=datetime.now(UTC),
    )
    db.add(entry)
    await db.commit()
    return {"message": "İzleme geçmişine eklendi", "already_exists": False}
