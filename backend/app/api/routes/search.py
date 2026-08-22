"""
Semantic search endpoint — the core AI feature. Available to any
authenticated user; every query is logged for analytics ("most searched
queries").
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.document import SearchResponse
from app.services.search_service import semantic_search
from app.services.activity_service import log_activity

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(
    query: str = Query(..., min_length=1),
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = semantic_search(db, query, top_k=top_k)
    log_activity(db, current_user.id, "SEARCH", query)
    return SearchResponse(query=query, results=results)
