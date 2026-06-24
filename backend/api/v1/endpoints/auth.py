from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Response, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_db
from backend.core.deps import get_current_user_id
from backend.core.redis_client import blacklist_token
from backend.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_token
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
    Kullanıcı kayıt endpoint'i.
    """
    return await auth_service.register_user(db=db, user_in=user_in)


@router.post("/login", response_model=TokenResponse)
async def login(
    user_in: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Kullanıcı giriş endpoint'i. Web istemcileri için httpOnly cookie set eder;
    ayrıca mobil istemcilerin token'ı kendileri saklayabilmesi için body'de de döner.
    """
    user = await auth_service.login_user(db=db, credentials=user_in)
    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    is_production = get_settings().ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="none" if is_production else "lax",
        secure=is_production,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    authorization: str | None = Header(default=None),
    access_token: str | None = Cookie(default=None),
    user_id: int = Depends(get_current_user_id),
) -> None:
    token: str | None = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
    elif access_token:
        token = access_token

    if token:
        payload = verify_token(token)
        if payload:
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                remaining = int(exp - datetime.now(timezone.utc).timestamp())
                await blacklist_token(jti, remaining)

    response.delete_cookie(key="access_token", path="/")


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


@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    contents = await file.read()
    suffix = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".jpg"
    filename = f"{user_id}{suffix}"
    save_path = Path("backend/static/avatars") / filename
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(contents)

    avatar_url = f"/static/avatars/{filename}"
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
    user.avatar_url = avatar_url
    await db.commit()
    return {"avatar_url": avatar_url}
