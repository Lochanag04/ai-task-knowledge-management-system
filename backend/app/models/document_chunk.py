from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class DocumentChunk(Base):
    """
    A chunk of text extracted from a document. Each chunk maps 1:1 to a
    vector stored in the FAISS index (vector_index_id == position in index).
    Keeping the raw text in MySQL lets us return human-readable search
    results while FAISS only stores the numeric vectors.
    """
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    vector_index_id = Column(Integer, nullable=False, unique=True, index=True)

    document = relationship("Document", back_populates="chunks")
