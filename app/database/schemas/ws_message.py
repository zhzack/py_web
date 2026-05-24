from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


# --- V2 envelope ---

MessageType = Literal[
    "register", "heartbeat", "action", "ack", "error", "status", "sync", "dev_cmd"
]


class WsHeader(BaseModel):
    msg_id: str
    seq: int = 0
    timestamp: int = 0
    source: str = "web"
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    type: MessageType
    priority: int = 0
    ref_msg_id: Optional[str] = None


class WsRouting(BaseModel):
    target_devices: List[str] = Field(default_factory=list)
    broadcast: bool = False
    group: Optional[str] = None


class WsEnvelope(BaseModel):
    header: WsHeader
    routing: WsRouting = Field(default_factory=WsRouting)
    payload: Dict[str, Any] = Field(default_factory=dict)


# --- HTTP / 业务 ---


class ActionRequest(BaseModel):
    """HTTP /api/v2/action 请求体，服务端会自动包装为 envelope。"""
    device_id: Optional[str] = None  # 单设备
    target_devices: Optional[List[str]] = None  # 多设备
    group: Optional[str] = None
    broadcast: bool = False
    payload: Dict[str, Any]
    priority: int = 0
    timeout_ms: int = 2000  # 等待 ack 的超时


class ActionResult(BaseModel):
    msg_id: str
    device_id: str
    status: Literal["acked", "failed", "timeout"]
    exec_time_ms: Optional[int] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class ActionResponse(BaseModel):
    msg_id: str
    dispatched_to: List[str]
    results: List[ActionResult] = Field(default_factory=list)


# --- Action log ---


class ActionLogOut(BaseModel):
    id: int
    msg_id: str
    user_id: Optional[int]
    device_id: Optional[int]
    action_type: Optional[str]
    status: str
    exec_time_ms: Optional[int]
    error_code: Optional[str]
    error_message: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
