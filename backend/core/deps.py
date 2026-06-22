from fastapi import Cookie, Header, HTTPException, status

from backend.core.redis_client import is_token_blacklisted
from backend.core.security import verify_token


async def get_current_user_id(
    authorization: str | None = Header(default=None),
    access_token: str | None = Cookie(default=None),
) -> int:
    token: str | None = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yetkilendirme gerekli.",
        )

    payload = verify_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya süresi dolmuş token.",
        )

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token iptal edilmiş. Lütfen tekrar giriş yapın.",
        )

    try:
        return int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz token.",
        ) from exc
