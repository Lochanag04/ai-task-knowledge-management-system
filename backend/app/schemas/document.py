from datetime import datetime
from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class SearchResultItem(BaseModel):
    document_id: int
    document_title: str
    chunk_text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
