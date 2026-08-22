import { useEffect, useState } from "react";
import api from "../api/axios";

export default function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/analytics")
      .then(({ data }) => setAnalytics(data))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load analytics"));
  }, []);

  if (error) return <div className="card error-text">{error}</div>;
  if (!analytics) return <div className="card muted">Loading analytics...</div>;

  return (
    <div className="card">
      <h2>Analytics</h2>

      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-value">{analytics.total_tasks}</span>
          <span className="stat-label">Total Tasks</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{analytics.completed_tasks}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{analytics.pending_tasks}</span>
          <span className="stat-label">Pending</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{analytics.total_documents}</span>
          <span className="stat-label">Documents</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{analytics.total_users}</span>
          <span className="stat-label">Users</span>
        </div>
      </div>

      <h3>Most Searched Queries</h3>
      {analytics.top_search_queries.length === 0 ? (
        <p className="muted">No searches logged yet.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Query</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            {analytics.top_search_queries.map((q, idx) => (
              <tr key={idx}>
                <td>{q.query}</td>
                <td>{q.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
