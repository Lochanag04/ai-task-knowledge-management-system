import { useEffect, useState } from "react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

export default function Tasks() {
  const { user } = useAuth();
  const isAdmin = user.role === "admin";

  const [tasks, setTasks] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // admin-only "create task" form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignedTo, setAssignedTo] = useState("");

  const loadTasks = async (status) => {
    setLoading(true);
    try {
      const params = {};
      if (status) params.status = status;
      const { data } = await api.get("/tasks", { params });
      setTasks(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks(statusFilter);
    if (isAdmin) {
      api.get("/auth/users").then(({ data }) => setUsers(data));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter]);

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.post("/tasks", {
        title,
        description,
        assigned_to: Number(assignedTo),
      });
      setTitle("");
      setDescription("");
      setAssignedTo("");
      loadTasks(statusFilter);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create task");
    }
  };

  const handleComplete = async (taskId) => {
    try {
      await api.patch(`/tasks/${taskId}/status`, { status: "completed" });
      loadTasks(statusFilter);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to update task");
    }
  };

  return (
    <div className="card">
      <h2>Tasks</h2>

      {isAdmin && (
        <form className="task-form" onSubmit={handleCreateTask}>
          <h3>Assign a new task</h3>
          <div className="form-row">
            <input
              placeholder="Task title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <select
              value={assignedTo}
              onChange={(e) => setAssignedTo(e.target.value)}
              required
            >
              <option value="">Assign to...</option>
              {users
                .filter((u) => u.role === "user")
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.email})
                  </option>
                ))}
            </select>
          </div>
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <button className="btn btn-primary" type="submit">
            Create Task
          </button>
        </form>
      )}

      <div className="filter-row">
        <label>Filter by status: </label>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {error && <div className="error-text">{error}</div>}
      {loading && <p className="muted">Loading...</p>}

      <table className="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Description</th>
            {isAdmin && <th>Assigned To (user id)</th>}
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id}>
              <td>{t.id}</td>
              <td>{t.title}</td>
              <td>{t.description || "-"}</td>
              {isAdmin && <td>{t.assigned_to}</td>}
              <td>
                <span className={`status-badge status-${t.status}`}>{t.status}</span>
              </td>
              <td>
                {!isAdmin && t.status === "pending" && (
                  <button className="btn btn-small" onClick={() => handleComplete(t.id)}>
                    Mark Completed
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
