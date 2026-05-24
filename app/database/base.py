# app/database/base.py
# 汇总所有 ORM 模型，便于 Alembic 与 Base.metadata.create_all 使用。
from app.database.base_class import Base  # noqa: F401

# 旧业务模型
from app.database.models.vehicle import VehicleModel  # noqa: F401

# HID Gateway 模型
from app.database.models.user import User  # noqa: F401
from app.database.models.device import Device, DeviceConnection  # noqa: F401
from app.database.models.action_log import ActionLog  # noqa: F401
from app.database.models.macro import Macro  # noqa: F401
from app.database.models.device_group import DeviceGroup, DeviceGroupMember  # noqa: F401
