from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user_preference import UserPreference


async def save_user_preferences(
    db: AsyncSession, user_id: int, genres: list[str]
) -> None:
    await db.execute(delete(UserPreference).where(UserPreference.user_id == user_id))

    for genre in genres:
        label = genre.strip()
        if not label:
            continue
        db.add(UserPreference(user_id=user_id, genre=label[:100], weight=1))

    await db.commit()
