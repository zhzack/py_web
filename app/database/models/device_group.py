from sqlalchemy import Column, BigInteger, String, TIMESTAMP, ForeignKey, text
from app.database.base_class import Base


class DeviceGroup(Base):
    __tablename__ = "device_groups"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    owner_user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(128), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))


class DeviceGroupMember(Base):
    __tablename__ = "device_group_members"

    group_id = Column(
        BigInteger,
        ForeignKey("device_groups.id", ondelete="CASCADE"),
        primary_key=True,
    )
    device_id = Column(
        BigInteger,
        ForeignKey("devices.id", ondelete="CASCADE"),
        primary_key=True,
    )
