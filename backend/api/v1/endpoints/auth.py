from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.core.redis_client import blacklist_token
from backend.core.security import create_access_token, verify_token
from backend.models.user import User
from backend.schemas.token import TokenResponse
from backend.schemas.user import UserCreate, UserLogin, UserRead
from backend.services import auth_service


router = APIRouter()


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """
    User registration endpoint.
    """
    return await auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    User login endpoint.
    """
    user = await auth_service.login_user(db=db, credentials=user_in)
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    authorization: str | None = Header(default=None),
    user_id: int = Depends(get_current_user_id),
) -> None:
    if not authorization:
        return
    token = authorization.removeprefix("Bearer ").strip()
    payload = verify_token(token)
    if payload:
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            remaining = int(exp - datetime.now(timezone.utc).timestamp())
            await blacklist_token(jti, remaining)


@router.get("/me", response_model=UserRead)
async def get_me(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
) -> UserRead:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı",
        )
    return user
