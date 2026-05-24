from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.crud import user as crud_user
from app.database.schemas.user import UserCreate, UserOut, Token
from app.core.security import create_access_token, get_current_user
from app.database.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if crud_user.get_by_username(db, payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "username exists")
    user = crud_user.create(db, payload.username, payload.password, payload.role)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud_user.authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    token, expires_in = create_access_token(sub=str(user.id), role=user.role)
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
