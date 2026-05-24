"""JWT 鉴权 + 密码哈希 + FastAPI 依赖。"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config.config import settings
from app.database.session import get_db
from app.database.models.user import User

import bcrypt


def hash_password(plain: str) -> str:
    pw = plain.encode("utf-8")[:72]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
    except Exception:
        return False


# ----- JWT -----
_JWT_SECRET = settings.JWT_SECRET
_JWT_ALG = settings.JWT_ALGORITHM
_JWT_EXP_MIN = int(settings.JWT_EXPIRE_MINUTES)


def create_access_token(
    sub: str, role: str = "user", expires_minutes: Optional[int] = None
) -> tuple[str, int]:
    """返回 (token, expires_in_seconds)。"""
    exp_min = expires_minutes or _JWT_EXP_MIN
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=exp_min)
    payload = {
        "sub": str(sub),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALG)
    return token, exp_min * 60


def decode_token(token: str) -> dict:
    return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALG])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found"
        )
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin only")
    return user


async def ws_authenticate(websocket: WebSocket, db: Session) -> Optional[User]:
    """WebSocket 鉴权：从 query string `token=...` 取 JWT。

    失败时关闭连接并返回 None。
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return None
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError, TypeError):
        await websocket.close(code=4401)
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        await websocket.close(code=4401)
        return None
    return user
