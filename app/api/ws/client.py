"""浏览器 / 脚本 WS 端点：/ws/client。

用于实时下发 action + 订阅状态/日志推送（订阅 channel: status / logs / action_result）。
"""
import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.logger.logger import logger
from app.core.security import ws_authenticate
from app.database.session import SessionLocal
from app.services import dispatcher
from app.services.routing import resolve_targets

router = APIRouter()


@router.websocket("/ws/client")
async def client_ws(websocket: WebSocket):
    db = SessionLocal()
    user = await ws_authenticate(websocket, db)
    if user is None:
        try:
            db.close()
        except Exception:
            pass
        return

    await websocket.accept()
    logger.info(f"[ws/client] connected user={user.username}")

    try:
        while True:
            raw = await websocket.receive_json()
            header = raw.get("header", {}) if isinstance(raw, dict) else {}
            mtype = header.get("type") or raw.get("type")

            if mtype == "action":
                routing = raw.get("routing", {}) or {}
                payload = raw.get("payload", {}) or {}
                timeout_ms = int(header.get("timeout_ms") or 2000)

                targets = resolve_targets(
                    db,
                    user,
                    routing.get("target_devices"),
                    routing.get("group"),
                    bool(routing.get("broadcast")),
                )
                if not targets:
                    await websocket.send_json(_err(header.get("msg_id"), "E002", "no target device"))
                    continue

                # 并发投递所有目标
                results = await asyncio.gather(
                    *[
                        dispatcher.deliver_to_device(
                            db,
                            device_uuid=d,
                            payload=payload,
                            user_id=user.id,
                            timeout_ms=timeout_ms,
                        )
                        for d in targets
                    ]
                )
                await websocket.send_json(
                    {
                        "header": {
                            "msg_id": str(uuid.uuid4()),
                            "ref_msg_id": header.get("msg_id"),
                            "type": "ack",
                            "timestamp": int(datetime.utcnow().timestamp()),
                        },
                        "payload": {"results": results},
                    }
                )

            elif mtype == "ping":
                await websocket.send_json(
                    {"header": {"type": "pong", "msg_id": str(uuid.uuid4())}, "payload": {}}
                )
            else:
                logger.debug(f"[ws/client] unknown type={mtype}")

    except WebSocketDisconnect:
        logger.info(f"[ws/client] disconnected user={user.username}")
    except Exception as e:
        logger.exception(f"[ws/client] error: {e}")
    finally:
        try:
            db.close()
        except Exception:
            pass


def _err(ref_msg_id, code, message):
    return {
        "header": {
            "msg_id": str(uuid.uuid4()),
            "ref_msg_id": ref_msg_id,
            "type": "error",
            "timestamp": int(datetime.utcnow().timestamp()),
        },
        "payload": {"code": code, "message": message},
    }
