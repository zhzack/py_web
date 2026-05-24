from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["admin", "user"] = "user"


class UserOut(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
