"""
Basic analytics dashboard data. Admin-only.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_role
from app.schemas.analytics import AnalyticsOut
from app.services.analytics_service import get_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsOut)
def analytics(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    return get_analytics(db)
