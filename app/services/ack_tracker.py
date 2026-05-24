"""ACK 追踪器：等待设备 ACK，超时抛出 TimeoutError。"""
import asyncio
from typing import Optional


class AckTracker:
    def __init__(self) -> None:
        self._pending: dict[str, asyncio.Future] = {}

    async def expect(self, msg_id: str, timeout: float) -> dict:
        """等待 ACK；超时抛 asyncio.TimeoutError。返回 ack 的 payload dict。"""
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[msg_id] = fut
        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        finally:
            self._pending.pop(msg_id, None)

    def resolve(self, ref_msg_id: str, ack_payload: dict) -> bool:
        fut = self._pending.get(ref_msg_id)
        if fut and not fut.done():
            fut.set_result(ack_payload)
            return True
        return False

    def pending_count(self) -> int:
        return len(self._pending)


ack_tracker = AckTracker()
