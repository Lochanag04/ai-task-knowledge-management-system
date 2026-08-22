import { useState } from "react";
import api from "../api/axios";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const { data } = await api.get("/search", { params: { query, top_k: 5 } });
      setResults(data.results);
    } catch (err) {
      setError(err.response?.data?.detail || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>AI Semantic Search</h2>
      <p className="muted">
        Search runs against a local embedding model (sentence-transformers) and a
        FAISS vector index built from every uploaded document — no external LLM
        call is required for retrieval.
      </p>

      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="Ask something, e.g. 'refund policy'..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <div className="error-text">{error}</div>}

      {results && results.length === 0 && (
        <p className="muted">No results found. Try uploading documents first.</p>
      )}

      <div className="results-list">
        {results?.map((r, idx) => (
          <div key={idx} className="result-item">
            <div className="result-header">
              <strong>{r.document_title}</strong>
              <span className="score-badge">score: {r.score}</span>
            </div>
            <p>{r.chunk_text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
