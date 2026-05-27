from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.database.session import get_db
from app.database.crud import device_group as crud_group
from app.database.schemas.device_group import (
    DeviceGroupCreate,
    DeviceGroupUpdate,
    DeviceGroupOut,
    AddDevicesRequest,
    DispatchRequest,
)
from app.core.security import get_current_user
from app.database.models.user import User
from app.services.dispatcher import deliver_to_device

router = APIRouter()


@router.post("", response_model=DeviceGroupOut, status_code=201)
@router.post("/", response_model=DeviceGroupOut, status_code=201)
def create_group(
    payload: DeviceGroupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_group.create_group(db, user.id, payload.name)


@router.get("", response_model=List[DeviceGroupOut])
@router.get("/", response_model=List[DeviceGroupOut])
def list_groups(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_group.list_for_user(db, user.id, user.role)


@router.get("/{group_id}", response_model=DeviceGroupOut)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    return group


@router.put("/{group_id}", response_model=DeviceGroupOut)
def update_group(
    group_id: int,
    payload: DeviceGroupUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    try:
        return crud_group.update_group(db, group_id, payload.name)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    crud_group.delete_group(db, group_id)


@router.get("/{group_id}/devices")
def get_group_devices(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    devices = crud_group.get_devices_in_group(db, group_id)
    return {"devices": [d.id for d in devices]}


@router.post("/{group_id}/members", status_code=204)
def add_devices(
    group_id: int,
    payload: AddDevicesRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    crud_group.add_devices_to_group(db, group_id, payload.device_ids)


@router.delete("/{group_id}/members/{device_id}", status_code=204)
def remove_device(
    group_id: int,
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")
    crud_group.remove_device_from_group(db, group_id, device_id)


@router.post("/{group_id}/dispatch")
async def dispatch_to_group(
    group_id: int,
    payload: DispatchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = crud_group.get_by_id(db, group_id)
    if not group:
        raise HTTPException(404, "group not found")
    if user.role != "admin" and group.owner_user_id != user.id:
        raise HTTPException(403, "not your group")

    devices = crud_group.get_devices_in_group(db, group_id)
    if not devices:
        return {"results": [], "summary": {"total": 0, "success": 0, "failed": 0}}

    tasks = [
        deliver_to_device(
            db,
            device_uuid=dev.device_uuid,
            payload=payload.payload,
            user_id=user.id,
            timeout_ms=payload.timeout_ms,
        )
        for dev in devices
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    formatted_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            formatted_results.append({
                "device_id": devices[i].device_uuid,
                "status": "error",
                "error_message": str(result),
            })
        else:
            formatted_results.append(result)

    success_count = sum(1 for r in formatted_results if r.get("status") == "acked")
    failed_count = len(formatted_results) - success_count

    return {
        "results": formatted_results,
        "summary": {
            "total": len(formatted_results),
            "success": success_count,
            "failed": failed_count,
        },
    }
