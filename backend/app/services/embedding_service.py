"""
Core AI logic for the whole system.

- Loads a local sentence-transformers model (no external LLM API calls).
- Maintains a single FAISS index on disk (IndexFlatIP over L2-normalised
  vectors == cosine similarity search).
- Every document chunk gets appended to the index; the index position
  (`vector_index_id`) is stored on the DocumentChunk row in MySQL so we can
  map a FAISS hit back to its source text.

This module is intentionally the only place that talks to FAISS / the
embedding model, so the rest of the app never has to know how semantic
search is implemented under the hood.
"""
import os
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings

_lock = threading.Lock()


class EmbeddingService:
    _model = None
    _index = None
    _dimension = None

    INDEX_FILENAME = "faiss_index.bin"

    def __init__(self):
        os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)
        self._index_path = os.path.join(settings.VECTOR_STORE_DIR, self.INDEX_FILENAME)
        self._load_model()
        self._load_or_create_index()

    # ---------- lazy singletons ----------
    def _load_model(self):
        if EmbeddingService._model is None:
            EmbeddingService._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            EmbeddingService._dimension = EmbeddingService._model.get_sentence_embedding_dimension()

    def _load_or_create_index(self):
        if EmbeddingService._index is not None:
            return
        if os.path.exists(self._index_path):
            EmbeddingService._index = faiss.read_index(self._index_path)
        else:
            # Inner product on normalised vectors == cosine similarity
            EmbeddingService._index = faiss.IndexFlatIP(EmbeddingService._dimension)

    # ---------- helpers ----------
    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        vectors = vectors.astype("float32")
        faiss.normalize_L2(vectors)
        return vectors

    def _persist(self):
        faiss.write_index(self._index, self._index_path)

    # ---------- public API ----------
    def add_chunks(self, chunks: list[str]) -> list[int]:
        """
        Embeds and appends `chunks` to the FAISS index.
        Returns the list of index positions assigned to each chunk, in order,
        so the caller can store them as DocumentChunk.vector_index_id.
        """
        if not chunks:
            return []
        with _lock:
            vectors = self._embed(chunks)
            start_id = self._index.ntotal
            self._index.add(vectors)
            self._persist()
            return list(range(start_id, start_id + len(chunks)))

    def search(self, query: str, top_k: int = 5) -> list[tuple[int, float]]:
        """
        Returns a list of (vector_index_id, similarity_score) tuples,
        best match first.
        """
        with _lock:
            if self._index.ntotal == 0:
                return []
            query_vector = self._embed([query])
            top_k = min(top_k, self._index.ntotal)
            scores, ids = self._index.search(query_vector, top_k)
            results = []
            for idx, score in zip(ids[0], scores[0]):
                if idx == -1:
                    continue
                results.append((int(idx), float(score)))
            return results


# Single shared instance used across the app (model + index loaded once)
embedding_service = EmbeddingService()
