import logging
from typing import Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.core.redis_client import get_redis

logger = logging.getLogger(__name__)

_MAX_REQUESTS = 300
_WINDOW_SECONDS = 60
_EXEMPT_PATHS = {"/docs", "/redoc", "/openapi.json", "/health"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Dakikada _MAX_REQUESTS isteğe izin ver. Redis kapalıysa atlanır."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in _EXEMPT_PATHS:
            return await call_next(request)

        redis = await get_redis()
        if not redis:
            return await call_next(request)

        forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        client_ip = (
            forwarded_for
            or request.headers.get("X-Real-IP", "").strip()
            or (request.client.host if request.client else "unknown")
        )
        key = f"rate_limit:{client_ip}"

        try:
            current = await redis.get(key)
            if current and int(current) >= _MAX_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Çok fazla istek. Lütfen bekleyin."},
                )
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, _WINDOW_SECONDS)
            await pipe.execute()
        except Exception as exc:
            logger.warning("Rate limiter Redis hatası: %s", exc)

        return await call_next(request)
