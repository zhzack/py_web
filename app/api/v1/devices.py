from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.database.crud import device as crud_device
from app.database.schemas.device import DeviceCreate, DeviceOut
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
def list_online(user: User = Depends(get_current_user)):
    return {"online": device_registry.list_online()}


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
