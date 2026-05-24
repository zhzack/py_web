from sqlalchemy.orm import Session
from app.database.models.macro import Macro


def get(db: Session, macro_id: int) -> Macro | None:
    return db.query(Macro).filter(Macro.id == macro_id).first()


def list_for_user(db: Session, user_id: int) -> list[Macro]:
    return db.query(Macro).filter(Macro.user_id == user_id).order_by(Macro.id.desc()).all()


def create(db: Session, user_id: int, name: str, steps: list[dict]) -> Macro:
    m = Macro(user_id=user_id, name=name, content_json={"steps": steps})
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


def delete(db: Session, macro_id: int, user_id: int) -> bool:
    m = db.query(Macro).filter(Macro.id == macro_id, Macro.user_id == user_id).first()
    if not m:
        return False
    db.delete(m)
    db.commit()
    return True
