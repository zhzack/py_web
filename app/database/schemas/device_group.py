from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DeviceGroupCreate(BaseModel):
    name: str


class DeviceGroupUpdate(BaseModel):
    name: str


class DeviceGroupOut(BaseModel):
    id: int
    owner_user_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceGroupWithDevices(DeviceGroupOut):
    device_ids: List[int]


class AddDevicesRequest(BaseModel):
    device_ids: List[int]


class DispatchRequest(BaseModel):
    payload: dict
    timeout_ms: Optional[int] = 2000
