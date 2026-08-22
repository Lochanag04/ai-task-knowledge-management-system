from datetime import datetime
from pydantic import BaseModel


class ActivityLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    details: str | None
    created_at: datetime

    class Config:
        from_attributes = True
