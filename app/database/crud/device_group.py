from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database.models.device_group import DeviceGroup, DeviceGroupMember
from app.database.models.device import Device


def create_group(db: Session, owner_user_id: int, name: str) -> DeviceGroup:
    group = DeviceGroup(owner_user_id=owner_user_id, name=name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def list_for_user(db: Session, user_id: int, role: str) -> list[DeviceGroup]:
    q = db.query(DeviceGroup)
    if role != "admin":
        q = q.filter(DeviceGroup.owner_user_id == user_id)
    return q.order_by(DeviceGroup.created_at.desc()).all()


def get_by_id(db: Session, group_id: int) -> DeviceGroup | None:
    return db.query(DeviceGroup).filter(DeviceGroup.id == group_id).first()


def update_group(db: Session, group_id: int, name: str) -> DeviceGroup:
    group = get_by_id(db, group_id)
    if not group:
        raise ValueError("Group not found")
    group.name = name
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group_id: int) -> None:
    group = get_by_id(db, group_id)
    if group:
        db.delete(group)
        db.commit()


def get_devices_in_group(db: Session, group_id: int) -> list[Device]:
    return (
        db.query(Device)
        .join(DeviceGroupMember, Device.id == DeviceGroupMember.device_id)
        .filter(DeviceGroupMember.group_id == group_id)
        .all()
    )


def add_devices_to_group(db: Session, group_id: int, device_ids: list[int]) -> None:
    for device_id in device_ids:
        existing = (
            db.query(DeviceGroupMember)
            .filter(
                and_(
                    DeviceGroupMember.group_id == group_id,
                    DeviceGroupMember.device_id == device_id,
                )
            )
            .first()
        )
        if not existing:
            member = DeviceGroupMember(group_id=group_id, device_id=device_id)
            db.add(member)
    db.commit()


def remove_device_from_group(db: Session, group_id: int, device_id: int) -> None:
    member = (
        db.query(DeviceGroupMember)
        .filter(
            and_(
                DeviceGroupMember.group_id == group_id,
                DeviceGroupMember.device_id == device_id,
            )
        )
        .first()
    )
    if member:
        db.delete(member)
        db.commit()
