from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.models.watchlist import Watchlist
from backend.schemas.movie import MovieRead, WatchlistItemRead


router = APIRouter()


@router.get("/", response_model=list[WatchlistItemRead])
async def get_my_watchlist(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> list[WatchlistItemRead]:
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == user_id)
        .options(selectinload(Watchlist.movie))
        .order_by(Watchlist.added_at.desc())
    )
    entries = result.scalars().all()
    items: list[WatchlistItemRead] = []
    for entry in entries:
        if entry.movie is None:
            continue
        movie_data = MovieRead.model_validate(entry.movie).model_dump()
        items.append(WatchlistItemRead(**movie_data, added_at=entry.added_at))
    return items


@router.get("/{movie_id}/status")
async def check_watchlist_status(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id,
        )
    )
    return {"in_watchlist": result.scalar_one_or_none() is not None}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    movie_id = payload.get("movie_id")
    if not movie_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="movie_id gerekli",
        )

    result = await db.execute(
        select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id,
        )
    )
    if result.scalar_one_or_none():
        return {"message": "Zaten listede", "already_exists": True}

    entry = Watchlist(
        user_id=user_id,
        movie_id=int(movie_id),
        added_at=datetime.now(UTC),
    )
    db.add(entry)
    await db.commit()
    return {"message": "Listeye eklendi", "already_exists": False}


@router.delete("/{movie_id}")
async def remove_from_watchlist(
    movie_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> dict:
    result = await db.execute(
        select(Watchlist).where(
            Watchlist.user_id == user_id,
            Watchlist.movie_id == movie_id,
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listede bulunamadı",
        )
    await db.delete(entry)
    await db.commit()
    return {"message": "Listeden çıkarıldı"}
