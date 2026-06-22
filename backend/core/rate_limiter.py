import logging
from typing import Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.core.redis_client import get_redis

logger = logging.getLogger(__name__)

_MAX_REQUESTS = 60
_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Dakikada _MAX_REQUESTS isteğe izin ver. Redis kapalıysa atlanır."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        redis = await get_redis()
        if not redis:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
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
