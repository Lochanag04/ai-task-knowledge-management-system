import { useState } from "react";
import Navbar from "../components/Navbar";
import Documents from "./Documents";
import Tasks from "./Tasks";
import Search from "./Search";

const TABS = [
  { key: "search", label: "Search" },
  { key: "tasks", label: "My Tasks" },
  { key: "documents", label: "Documents" },
];

export default function UserDashboard() {
  const [tab, setTab] = useState("search");

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

        {tab === "search" && <Search />}
        {tab === "tasks" && <Tasks />}
        {tab === "documents" && <Documents />}
      </div>
    </div>
  );
}
