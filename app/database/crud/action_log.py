from sqlalchemy.orm import Session
from app.database.models.action_log import ActionLog


def create_pending(
    db: Session,
    msg_id: str,
    user_id: int | None,
    device_id: int | None,
    action_type: str,
    payload: dict,
) -> ActionLog:
    log = ActionLog(
        msg_id=msg_id,
        user_id=user_id,
        device_id=device_id,
        action_type=action_type,
        payload_json=payload,
        status="pending",
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def mark_sent(db: Session, msg_id: str) -> None:
    db.query(ActionLog).filter(ActionLog.msg_id == msg_id).update({"status": "sent"})
    db.commit()


def mark_acked(db: Session, msg_id: str, exec_time_ms: int | None) -> None:
    db.query(ActionLog).filter(ActionLog.msg_id == msg_id).update(
        {"status": "acked", "exec_time_ms": exec_time_ms}
    )
    db.commit()


def mark_failed(
    db: Session, msg_id: str, code: str | None = None, message: str | None = None
) -> None:
    db.query(ActionLog).filter(ActionLog.msg_id == msg_id).update(
        {"status": "failed", "error_code": code, "error_message": message}
    )
    db.commit()


def list_recent(
    db: Session, user_id: int | None = None, limit: int = 100
) -> list[ActionLog]:
    q = db.query(ActionLog)
    if user_id is not None:
        q = q.filter(ActionLog.user_id == user_id)
    return q.order_by(ActionLog.id.desc()).limit(limit).all()
