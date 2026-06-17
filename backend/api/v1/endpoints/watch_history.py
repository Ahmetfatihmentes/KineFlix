from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.models.watch_history import WatchHistory
from backend.schemas.movie import MovieRead


router = APIRouter()


@router.get("/", response_model=list[MovieRead])
async def list_watch_history(db: AsyncSession = Depends(get_db)) -> list[MovieRead]:
    """
    List movies from watch history (placeholder until auth is wired).
    """
    statement = (
        select(WatchHistory)
        .options(selectinload(WatchHistory.movie))
        .limit(50)
    )
    result = await db.execute(statement)
    entries = result.scalars().all()
    return [entry.movie for entry in entries if entry.movie is not None]
