from sqlalchemy import (
    Column, BigInteger, String, Integer, JSON, Enum, CHAR, TIMESTAMP, text,
)
from app.database.base_class import Base


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    msg_id = Column(CHAR(36), unique=True, nullable=False)
    user_id = Column(BigInteger, nullable=True)
    device_id = Column(BigInteger, nullable=True)
    action_type = Column(String(64))
    payload_json = Column(JSON)
    status = Column(
        Enum("pending", "sent", "acked", "failed"),
        nullable=False,
        server_default="pending",
    )
    exec_time_ms = Column(Integer, nullable=True)
    error_code = Column(String(16), nullable=True)
    error_message = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
