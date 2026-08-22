"""
Business logic for document ingestion: save the file, extract text,
chunk it, embed the chunks, and persist metadata rows in MySQL.
"""
import os
import uuid

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embedding_service import embedding_service
from app.utils.file_parser import extract_text, chunk_text


ALLOWED_EXTENSIONS = {"txt", "pdf"}


def save_uploaded_file(file: UploadFile) -> tuple[str, str, str]:
    """
    Saves the uploaded file to disk under a unique name.
    Returns (stored_filename, filepath, file_type).
    """
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: .{ext}. Allowed: {ALLOWED_EXTENSIONS}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, stored_filename)

    with open(filepath, "wb") as out:
        out.write(file.file.read())

    return stored_filename, filepath, ext


def ingest_document(db: Session, file: UploadFile, title: str, uploaded_by: int) -> Document:
    """
    Full ingestion pipeline: store file -> extract text -> chunk ->
    embed (FAISS) -> persist Document + DocumentChunk rows.
    """
    stored_filename, filepath, file_type = save_uploaded_file(file)

    document = Document(
        title=title,
        filename=stored_filename,
        original_filename=file.filename,
        filepath=filepath,
        file_type=file_type,
        uploaded_by=uploaded_by,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    raw_text = extract_text(filepath, file_type)
    chunks = chunk_text(raw_text)

    if chunks:
        vector_ids = embedding_service.add_chunks(chunks)
        for text_chunk, vector_id in zip(chunks, vector_ids):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    chunk_text=text_chunk,
                    vector_index_id=vector_id,
                )
            )
        db.commit()

    return document
