import { useState } from "react";
import Navbar from "../components/Navbar";
import Documents from "./Documents";
import Tasks from "./Tasks";
import Analytics from "./Analytics";
import Search from "./Search";

const TABS = [
  { key: "documents", label: "Documents" },
  { key: "tasks", label: "Tasks" },
  { key: "search", label: "Search" },
  { key: "analytics", label: "Analytics" },
];

export default function AdminDashboard() {
  const [tab, setTab] = useState("documents");

  return (
    <div>
      <Navbar />
      <div className="page-body">
        <div className="tabs">
          {TABS.map((t) => (
            <button
              key={t.key}
              className={`tab-btn ${tab === t.key ? "active" : ""}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "documents" && <Documents />}
        {tab === "tasks" && <Tasks />}
        {tab === "search" && <Search />}
        {tab === "analytics" && <Analytics />}
      </div>
    </div>
  );
}
