"""
Turns a user's free-text query into semantic search results by delegating
to the embedding service and re-joining hits with their MySQL rows.
"""
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.services.embedding_service import embedding_service


def semantic_search(db: Session, query: str, top_k: int = 5) -> list[dict]:
    hits = embedding_service.search(query, top_k=top_k)
    if not hits:
        return []

    vector_ids = [vid for vid, _ in hits]
    score_by_vector_id = {vid: score for vid, score in hits}

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.vector_index_id.in_(vector_ids))
        .all()
    )
    chunk_by_vector_id = {c.vector_index_id: c for c in chunks}

    document_ids = {c.document_id for c in chunks}
    documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
    document_by_id = {d.id: d for d in documents}

    results = []
    for vid in vector_ids:
        chunk = chunk_by_vector_id.get(vid)
        if not chunk:
            continue
        doc = document_by_id.get(chunk.document_id)
        results.append(
            {
                "document_id": chunk.document_id,
                "document_title": doc.title if doc else "Unknown",
                "chunk_text": chunk.chunk_text,
                "score": round(score_by_vector_id[vid], 4),
            }
        )
    # results already come back from FAISS ranked best-first; sort defensively
    results.sort(key=lambda r: r["score"], reverse=True)
    return results
