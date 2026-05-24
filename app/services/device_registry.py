"""在线设备注册表（进程内）。

维护 device_uuid -> WebSocket 映射。
二期可同步到 Redis SET `device:online` 让多实例可见。
"""
from typing import Optional
from fastapi import WebSocket


class DeviceRegistry:
    def __init__(self) -> None:
        self._live: dict[str, WebSocket] = {}

    def register(self, device_uuid: str, ws: WebSocket) -> None:
        self._live[device_uuid] = ws

    def unregister(self, device_uuid: str) -> None:
        self._live.pop(device_uuid, None)

    def get(self, device_uuid: str) -> Optional[WebSocket]:
        return self._live.get(device_uuid)

    def is_online(self, device_uuid: str) -> bool:
        return device_uuid in self._live

    def list_online(self) -> list[str]:
        return list(self._live.keys())


device_registry = DeviceRegistry()
