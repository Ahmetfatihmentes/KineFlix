from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.schemas.user_preference import PreferencesCreate, PreferencesMessage
from backend.services import user_service


router = APIRouter()


@router.post("/preferences", response_model=PreferencesMessage)
async def save_preferences(
    body: PreferencesCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> PreferencesMessage:
    await user_service.save_user_preferences(db=db, user_id=user_id, genres=body.genres)
    return PreferencesMessage(message="Tercihler kaydedildi")
