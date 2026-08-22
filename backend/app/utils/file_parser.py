"""
Extracts plain text from uploaded .txt / .pdf files and splits it into
overlapping chunks suitable for embedding.
"""
from pypdf import PdfReader


def extract_text(filepath: str, file_type: str) -> str:
    if file_type == "pdf":
        reader = PdfReader(filepath)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages)
    elif file_type == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Simple word-based sliding-window chunker. Keeps chunks small enough for
    good embedding quality while overlap preserves context across chunk
    boundaries.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks
