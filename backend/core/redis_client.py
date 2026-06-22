import logging

import redis.asyncio as aioredis

from backend.core.config import get_settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis
    url = get_settings().REDIS_URL
    if not url:
        logger.info("REDIS_URL tanımlı değil, Redis devre dışı.")
        return
    try:
        _redis = aioredis.from_url(url, decode_responses=True)
        await _redis.ping()
        logger.info("Redis bağlantısı kuruldu.")
    except Exception as exc:
        logger.warning("Redis bağlantısı kurulamadı, token iptali devre dışı: %s", exc)
        _redis = None


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def blacklist_token(jti: str, ttl_seconds: int) -> None:
    if not _redis or ttl_seconds <= 0:
        return
    try:
        await _redis.setex(f"blacklist:{jti}", ttl_seconds, "1")
    except Exception as exc:
        logger.warning("Token kara listeye eklenemedi: %s", exc)


async def is_token_blacklisted(jti: str) -> bool:
    if not _redis:
        return False
    try:
        return await _redis.exists(f"blacklist:{jti}") > 0
    except Exception as exc:
        logger.warning("Redis kara liste kontrolü başarısız: %s", exc)
        return False
