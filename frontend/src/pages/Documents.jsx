import { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Documents() {
  const { user } = useAuth();
  const isAdmin = user.role === "admin";

  const [documents, setDocuments] = useState([]);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const loadDocuments = async () => {
    const { data } = await api.get("/documents");
    setDocuments(data);
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("file", file);
      await api.post("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setTitle("");
      setFile(null);
      e.target.reset();
      loadDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card">
      <h2>Knowledge Base Documents</h2>

      {isAdmin && (
        <form className="task-form" onSubmit={handleUpload}>
          <h3>Upload a new document</h3>
          <div className="form-row">
            <input
              placeholder="Document title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setFile(e.target.files[0])}
              required
            />
          </div>
          <button className="btn btn-primary" type="submit" disabled={uploading}>
            {uploading ? "Uploading & embedding..." : "Upload"}
          </button>
        </form>
      )}

      {error && <div className="error-text">{error}</div>}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Original filename</th>
            <th>Type</th>
            <th>Uploaded</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((d) => (
            <tr key={d.id}>
              <td>{d.id}</td>
              <td>{d.title}</td>
              <td>{d.original_filename}</td>
              <td>{d.file_type}</td>
              <td>{new Date(d.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
