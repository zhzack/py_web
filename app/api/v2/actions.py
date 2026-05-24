"""V2 协议 HTTP 入口：与 WS /ws/client 等价的 action 下发能力。"""
import asyncio
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.crud import action_log as crud_action_log
from app.database.models.user import User
from app.database.schemas.ws_message import (
    ActionRequest, ActionResponse, ActionResult, ActionLogOut,
)
from app.database.session import get_db
from app.services import dispatcher
from app.services.routing import resolve_targets

router = APIRouter()


@router.post("/action", response_model=ActionResponse)
async def dispatch_action(
    payload: ActionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    targets = resolve_targets(
        db,
        user,
        [payload.device_id] if payload.device_id else payload.target_devices,
        payload.group,
        payload.broadcast,
    )
    if not targets:
        raise HTTPException(404, "no matching device")

    results = await asyncio.gather(
        *[
            dispatcher.deliver_to_device(
                db,
                device_uuid=d,
                payload=payload.payload,
                user_id=user.id,
                timeout_ms=payload.timeout_ms,
                priority=payload.priority,
            )
            for d in targets
        ]
    )
    return ActionResponse(
        msg_id=results[0]["msg_id"] if results else "",
        dispatched_to=targets,
        results=[ActionResult(**r) for r in results],
    )


@router.get("/logs", response_model=List[ActionLogOut])
def recent_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_action_log.list_recent(
        db,
        user_id=None if user.role == "admin" else user.id,
        limit=min(limit, 1000),
    )
