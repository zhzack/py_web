from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.database.crud import device as crud_device
from app.database.schemas.device import DeviceCreate, DeviceUpdate, DeviceOut
from app.core.security import get_current_user
from app.database.models.user import User
from app.services.device_registry import device_registry

router = APIRouter()


@router.get("", response_model=List[DeviceOut])
@router.get("/", response_model=List[DeviceOut])
def list_devices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_device.list_for_user(db, user.id, user.role)


@router.post("", response_model=DeviceOut, status_code=201)
@router.post("/", response_model=DeviceOut, status_code=201)
def create_device(
    payload: DeviceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if crud_device.get_by_uuid(db, payload.device_uuid):
        raise HTTPException(409, "device_uuid exists")
    return crud_device.create(
        db, payload.device_uuid, user.id, payload.name, payload.capabilities
    )


@router.get("/online")
def list_online(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    all_online = device_registry.list_online()
    if user.role == "admin":
        return {"online": all_online}
    visible_uuids = []
    for uuid in all_online:
        dev = crud_device.get_by_uuid(db, uuid)
        if dev and (dev.owner_user_id is None or dev.owner_user_id == user.id):
            visible_uuids.append(uuid)
    return {"online": visible_uuids}


@router.post("/{device_id}/claim", response_model=DeviceOut)
def claim_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return crud_device.claim_device(db, device_id, user.id)
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.put("/{device_id}", response_model=DeviceOut)
def update_device(
    device_id: int,
    payload: DeviceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dev = crud_device.get_by_id(db, device_id)
    if not dev:
        raise HTTPException(404, "device not found")
    if user.role != "admin" and dev.owner_user_id != user.id:
        raise HTTPException(403, "not your device")
    if payload.owner_user_id is not None and user.role != "admin":
        raise HTTPException(403, "only admin can reassign ownership")
    try:
        return crud_device.update_device(
            db,
            device_id,
            name=payload.name,
            capabilities=payload.capabilities,
            owner_user_id=payload.owner_user_id,
        )
    except ValueError as e:
        raise HTTPException(400, str(e))


@router.get("/{device_id}", response_model=DeviceOut)
def get_device(
    device_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dev = crud_device.get_by_id(db, device_id)
    if not dev:
        raise HTTPException(404, "device not found")
    if user.role != "admin" and dev.owner_user_id not in (None, user.id):
        raise HTTPException(403, "not your device")
    return dev
