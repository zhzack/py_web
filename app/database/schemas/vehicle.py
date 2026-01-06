from pydantic import BaseModel
from typing import Optional

class VehicleBase(BaseModel):
    model_name: str
    vehicle_code: str
    vin: str
    phase: Optional[str] = None
    configuration: Optional[str] = None
    chip_platform: Optional[str] = None
    wheel_size: Optional[int] = None
    has_data_device: bool = False
    current_status: str = "空闲"

class VehicleOut(VehicleBase):
    id: int

    class Config:
        from_attributes = True # 允许从 SQLAlchemy 模型转换