"""
Read-only view of the audit trail. Admin-only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_role
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogOut

router = APIRouter(prefix="/activity-logs", tags=["activity-logs"])


@router.get("", response_model=list[ActivityLogOut])
def list_activity_logs(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    return db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(200).all()
