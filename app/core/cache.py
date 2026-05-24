"""Redis 客户端工厂（用于队列二期 + 在线状态 + 幂等 set 等）。"""
from typing import Optional
import redis.asyncio as aioredis

from app.core.config.config import settings

_client: Optional[aioredis.Redis] = None


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
