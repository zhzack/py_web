import asyncio
from collections import defaultdict
from typing import AsyncGenerator


class LogBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    async def publish(self, execution_id: str, line: str):
        for queue in self.subscribers[execution_id]:
            await queue.put(line)

    async def subscribe(self, execution_id: str) -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        self.subscribers[execution_id].append(queue)
        try:
            while True:
                line = await queue.get()
                yield line
        finally:
            self.subscribers[execution_id].remove(queue)


log_bus = LogBus()
