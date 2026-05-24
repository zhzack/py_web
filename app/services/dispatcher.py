"""Dispatcher：核心动作分发逻辑。

- 给单个设备投递 envelope
- 等待 ACK（带超时 + 指数退避重试）
- 写入 action_logs
"""
import asyncio
import time
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.logger.logger import logger
from app.database.crud import action_log as crud_action_log
from app.database.crud import device as crud_device
from app.services.ack_tracker import ack_tracker
from app.services.device_registry import device_registry
from app.services.queue import queue_backend

_RETRY_DELAYS_MS = [100, 300, 900]  # 指数退避；总尝试 = 3 次


def build_envelope(
    *,
    msg_id: str,
    user_id: int | None,
    device_uuid: str,
    payload: dict,
    seq: int = 0,
    priority: int = 0,
    source: str = "web",
) -> dict:
    return {
        "header": {
            "msg_id": msg_id,
            "seq": seq,
            "timestamp": int(time.time()),
            "source": source,
            "user_id": str(user_id) if user_id else None,
            "device_id": device_uuid,
            "type": "action",
            "priority": priority,
        },
        "routing": {"target_devices": [device_uuid], "broadcast": False, "group": None},
        "payload": payload,
    }


async def deliver_to_device(
    db: Session,
    *,
    device_uuid: str,
    payload: dict,
    user_id: int | None,
    timeout_ms: int = 2000,
    priority: int = 0,
) -> dict:
    """投递 + 等待 ACK + 失败重试。返回 result dict。"""
    msg_id = str(uuid.uuid4())
    action_type = payload.get("type", "unknown")
    dev_row = crud_device.get_by_uuid(db, device_uuid)
    device_db_id = dev_row.id if dev_row else None

    crud_action_log.create_pending(
        db,
        msg_id=msg_id,
        user_id=user_id,
        device_id=device_db_id,
        action_type=action_type,
        payload=payload,
    )

    if not device_registry.is_online(device_uuid):
        crud_action_log.mark_failed(db, msg_id, code="E002", message="device offline")
        return {
            "msg_id": msg_id,
            "device_id": device_uuid,
            "status": "failed",
            "error_code": "E002",
            "error_message": "device offline",
        }

    envelope = build_envelope(
        msg_id=msg_id,
        user_id=user_id,
        device_uuid=device_uuid,
        payload=payload,
        priority=priority,
    )

    last_error: tuple[str, str] | None = None
    for attempt, _ in enumerate(_RETRY_DELAYS_MS):
        ws = device_registry.get(device_uuid)
        if ws is None:
            last_error = ("E002", "device offline")
            break
        try:
            await queue_backend.push(device_uuid, envelope)
            crud_action_log.mark_sent(db, msg_id)
        except Exception as e:
            logger.exception(f"[dispatcher] push failed: {e}")
            last_error = ("E003", "queue push error")
            continue

        try:
            ack = await ack_tracker.expect(msg_id, timeout=timeout_ms / 1000)
            exec_ms = int(ack.get("exec_time_ms", 0) or 0)
            status = ack.get("status", "ok")
            if status == "ok":
                crud_action_log.mark_acked(db, msg_id, exec_ms)
                return {
                    "msg_id": msg_id,
                    "device_id": device_uuid,
                    "status": "acked",
                    "exec_time_ms": exec_ms,
                }
            else:
                err = ack.get("error", {}) or {}
                last_error = (err.get("code", "E000"), err.get("message", "failed"))
                logger.warning(f"[dispatcher] device returned non-ok: {last_error}")
        except asyncio.TimeoutError:
            last_error = ("E006", f"ack timeout (attempt {attempt + 1})")
            logger.warning(f"[dispatcher] {last_error[1]} msg_id={msg_id}")
            # 指数退避
            await asyncio.sleep(_RETRY_DELAYS_MS[attempt] / 1000)

    code, message = last_error or ("E006", "retry exhausted")
    crud_action_log.mark_failed(db, msg_id, code=code, message=message)
    return {
        "msg_id": msg_id,
        "device_id": device_uuid,
        "status": "timeout" if code == "E006" else "failed",
        "error_code": code,
        "error_message": message,
    }
