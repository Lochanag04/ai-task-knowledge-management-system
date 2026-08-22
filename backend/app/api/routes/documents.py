"""
Document upload & listing. Upload is admin-only (building the knowledge
base); listing is available to any authenticated user.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import require_role, get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentOut
from app.services.document_service import ingest_document
from app.services.activity_service import log_activity

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut, status_code=201)
def upload_document(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    try:
        document = ingest_document(db, file, title, uploaded_by=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    log_activity(db, current_user.id, "DOCUMENT_UPLOAD", f"Uploaded '{document.title}' (doc #{document.id})")
    return document


@router.get("", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Document).order_by(Document.created_at.desc()).all()
