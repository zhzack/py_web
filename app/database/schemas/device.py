from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class DeviceBase(BaseModel):
    device_uuid: str = Field(..., max_length=128)
    name: Optional[str] = None
    capabilities: Optional[List[str]] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    capabilities: Optional[List[str]] = None


class DeviceOut(DeviceBase):
    id: int
    owner_user_id: Optional[int] = None
    status: Literal["offline", "online", "busy", "error"]
    last_online_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
