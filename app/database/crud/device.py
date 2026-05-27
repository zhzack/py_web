from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from app.database.models.device import Device, DeviceConnection


def get_by_uuid(db: Session, device_uuid: str) -> Device | None:
    return db.query(Device).filter(Device.device_uuid == device_uuid).first()


def get_by_id(db: Session, device_id: int) -> Device | None:
    return db.query(Device).filter(Device.id == device_id).first()


def list_for_user(db: Session, user_id: int, role: str) -> list[Device]:
    q = db.query(Device)
    if role != "admin":
        q = q.filter(or_(Device.owner_user_id == user_id, Device.owner_user_id.is_(None)))
    return q.order_by(Device.id.desc()).all()


def create(
    db: Session,
    device_uuid: str,
    owner_user_id: int | None,
    name: str | None = None,
    capabilities: list[str] | None = None,
) -> Device:
    dev = Device(
        device_uuid=device_uuid,
        owner_user_id=owner_user_id,
        name=name or device_uuid,
        capabilities=capabilities or [],
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev


def upsert_from_register(
    db: Session,
    device_uuid: str,
    name: str | None,
    capabilities: list[str] | None,
) -> Device:
    """设备 WS register 时调用：若不存在则创建，否则更新状态。"""
    dev = get_by_uuid(db, device_uuid)
    if dev is None:
        dev = Device(
            device_uuid=device_uuid,
            name=name or device_uuid,
            capabilities=capabilities or [],
            status="online",
            last_online_at=datetime.utcnow(),
        )
        db.add(dev)
    else:
        if name:
            dev.name = name
        if capabilities is not None:
            dev.capabilities = capabilities
        dev.status = "online"
        dev.last_online_at = datetime.utcnow()
    db.commit()
    db.refresh(dev)
    return dev


def mark_offline(db: Session, device_uuid: str) -> None:
    dev = get_by_uuid(db, device_uuid)
    if dev:
        dev.status = "offline"
        db.commit()


def claim_device(db: Session, device_id: int, user_id: int) -> Device:
    """Claim an unclaimed device. Raises if already owned."""
    dev = get_by_id(db, device_id)
    if not dev:
        raise ValueError("Device not found")
    if dev.owner_user_id is not None:
        raise ValueError("Device already claimed")
    dev.owner_user_id = user_id
    db.commit()
    db.refresh(dev)
    return dev


def update_device(
    db: Session,
    device_id: int,
    name: str | None = None,
    capabilities: list[str] | None = None,
    owner_user_id: int | None = None,
) -> Device:
    """Update device fields. Pass None to skip updating a field."""
    dev = get_by_id(db, device_id)
    if not dev:
        raise ValueError("Device not found")
    if name is not None:
        dev.name = name
    if capabilities is not None:
        dev.capabilities = capabilities
    if owner_user_id is not None:
        dev.owner_user_id = owner_user_id
    db.commit()
    db.refresh(dev)
    return dev


def record_connection(db: Session, device_id: int, ip: str | None, session_id: str) -> DeviceConnection:
    conn = DeviceConnection(device_id=device_id, ip=ip, session_id=session_id)
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return conn


def close_connection(db: Session, session_id: str) -> None:
    conn = (
        db.query(DeviceConnection)
        .filter(DeviceConnection.session_id == session_id, DeviceConnection.disconnected_at.is_(None))
        .first()
    )
    if conn:
        conn.disconnected_at = datetime.utcnow()
        db.commit()
