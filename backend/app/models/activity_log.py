from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ActivityLog(Base):
    """
    Generic audit trail. `action` is a short machine-readable tag such as
    'LOGIN', 'DOCUMENT_UPLOAD', 'TASK_UPDATE', 'SEARCH'.
    `details` holds free-form context (e.g. the search query text, or
    'task #4 -> completed').
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False, index=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")
