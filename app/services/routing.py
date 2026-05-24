"""路由引擎：解析 routing 字段为目标设备列表。"""
from typing import Iterable
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database.models.device import Device
from app.database.models.device_group import DeviceGroup, DeviceGroupMember
from app.database.models.user import User


def resolve_targets(
    db: Session,
    current_user: User,
    target_devices: Iterable[str] | None,
    group: str | None,
    broadcast: bool,
) -> list[str]:
    """返回 device_uuid 列表。优先级：target_devices > group > broadcast > 用户全部设备"""
    is_admin = current_user.role == "admin"

    def _filter_own(uuids: list[str]) -> list[str]:
        if is_admin:
            return uuids
        rows = (
            db.query(Device.device_uuid)
            .filter(
                Device.device_uuid.in_(uuids),
                or_(Device.owner_user_id == current_user.id, Device.owner_user_id.is_(None)),
            )
            .all()
        )
        return [r[0] for r in rows]

    if target_devices:
        return _filter_own(list(target_devices))

    if group:
        q = (
            db.query(Device.device_uuid)
            .join(DeviceGroupMember, DeviceGroupMember.device_id == Device.id)
            .join(DeviceGroup, DeviceGroup.id == DeviceGroupMember.group_id)
            .filter(DeviceGroup.name == group)
        )
        if not is_admin:
            q = q.filter(DeviceGroup.owner_user_id == current_user.id)
        return [r[0] for r in q.all()]

    if broadcast:
        q = db.query(Device.device_uuid).filter(Device.status == "online")
        if not is_admin:
            q = q.filter(Device.owner_user_id == current_user.id)
        return [r[0] for r in q.all()]

    # 兜底：用户自己拥有的全部设备
    q = db.query(Device.device_uuid)
    if not is_admin:
        q = q.filter(Device.owner_user_id == current_user.id)
    return [r[0] for r in q.all()]
