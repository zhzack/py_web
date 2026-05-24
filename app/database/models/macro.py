from sqlalchemy import Column, BigInteger, String, JSON, TIMESTAMP, ForeignKey, text
from app.database.base_class import Base


class Macro(Base):
    __tablename__ = "macros"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(128), nullable=False)
    content_json = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )
