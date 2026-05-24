from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class MacroStep(BaseModel):
    type: str
    # 其余字段不强约束，由 Executor 端识别
    key: Optional[str] = None
    content: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[int] = None
    delay_ms: Optional[int] = None
    interval_ms: Optional[int] = None


class MacroCreate(BaseModel):
    name: str = Field(..., max_length=128)
    steps: List[Dict[str, Any]]


class MacroOut(BaseModel):
    id: int
    user_id: int
    name: str
    content_json: Dict[str, Any]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
