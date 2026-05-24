from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.database.crud import macro as crud_macro
from app.database.schemas.macro import MacroCreate, MacroOut
from app.core.security import get_current_user
from app.database.models.user import User

router = APIRouter()


@router.get("", response_model=List[MacroOut])
@router.get("/", response_model=List[MacroOut])
def list_macros(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_macro.list_for_user(db, user.id)


@router.post("", response_model=MacroOut, status_code=201)
@router.post("/", response_model=MacroOut, status_code=201)
def create_macro(
    payload: MacroCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return crud_macro.create(db, user.id, payload.name, payload.steps)


@router.delete("/{macro_id}", status_code=204)
def delete_macro(
    macro_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    ok = crud_macro.delete(db, macro_id, user.id)
    if not ok:
        raise HTTPException(404, "macro not found")
