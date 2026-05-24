"""队列后端抽象。

一期默认使用 MemoryBackend（asyncio.Queue per device）。
二期可通过 .env QUEUE_BACKEND=redis 切换。
"""
import asyncio
import json
from collections import defaultdict
from typing import Protocol, Optional

from app.core.config.config import settings


class QueueBackend(Protocol):
    async def push(self, device_id: str, envelope: dict) -> None: ...
    async def pop(self, device_id: str) -> Optional[dict]: ...
    async def size(self, device_id: str) -> int: ...


class MemoryBackend:
    """asyncio.Queue per device，进程内可用。"""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def push(self, device_id: str, envelope: dict) -> None:
        await self._queues[device_id].put(envelope)

    async def pop(self, device_id: str) -> Optional[dict]:
        return await self._queues[device_id].get()

    async def size(self, device_id: str) -> int:
        return self._queues[device_id].qsize()


class RedisBackend:
    """Redis List 实现（LPUSH / BRPOP）。"""

    def __init__(self) -> None:
        from app.core.cache import get_redis  # 延迟导入避免循环
        self._r = get_redis()

    @staticmethod
    def _key(device_id: str) -> str:
        return f"queue:device:{device_id}"

    async def push(self, device_id: str, envelope: dict) -> None:
        await self._r.lpush(self._key(device_id), json.dumps(envelope))

    async def pop(self, device_id: str) -> Optional[dict]:
        item = await self._r.brpop(self._key(device_id), timeout=0)
        if item is None:
            return None
        _key, raw = item
        return json.loads(raw)

    async def size(self, device_id: str) -> int:
        return int(await self._r.llen(self._key(device_id)))


def get_queue_backend() -> QueueBackend:
    backend = (settings.QUEUE_BACKEND or "memory").lower()
    if backend == "redis":
        return RedisBackend()
    return MemoryBackend()


# 单例（进程内共享一份）
queue_backend: QueueBackend = get_queue_backend()
