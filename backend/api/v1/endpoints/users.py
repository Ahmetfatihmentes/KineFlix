from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.models.user import User
from backend.schemas.user import UserRead, UserUpdate
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


@router.patch("/me", response_model=UserRead)
async def update_profile(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    await db.commit()
    await db.refresh(user)
    return user
