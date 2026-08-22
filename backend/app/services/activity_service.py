"""
Central place for writing audit-trail entries so every route logs
consistently instead of hand-rolling ActivityLog inserts everywhere.
"""
from sqlalchemy.orm import Session
from app.models.activity_log import ActivityLog


def log_activity(db: Session, user_id: int, action: str, details: str | None = None) -> None:
    entry = ActivityLog(user_id=user_id, action=action, details=details)
    db.add(entry)
    db.commit()
