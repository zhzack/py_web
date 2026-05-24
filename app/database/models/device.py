from sqlalchemy import (
    Column, BigInteger, String, JSON, Enum, TIMESTAMP, DateTime, ForeignKey, text,
)
from sqlalchemy.orm import relationship
from app.database.base_class import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device_uuid = Column(String(128), unique=True, nullable=False)
    owner_user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name = Column(String(128))
    capabilities = Column(JSON)
    status = Column(
        Enum("offline", "online", "busy", "error"),
        nullable=False,
        server_default="offline",
    )
    last_online_at = Column(DateTime, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    connections = relationship(
        "DeviceConnection", back_populates="device", cascade="all, delete-orphan"
    )


class DeviceConnection(Base):
    __tablename__ = "device_connections"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device_id = Column(
        BigInteger, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False
    )
    ip = Column(String(64))
    session_id = Column(String(128))
    connected_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    disconnected_at = Column(DateTime, nullable=True)

    device = relationship("Device", back_populates="connections")
