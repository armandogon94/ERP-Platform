import { useEffect, useState } from "react";
import ListPageShell from "../../components/ListPageShell";
import { type Task, fetchTasksApi } from "../../api/projects";

const STATUSES: { value: string; label: string }[] = [
  { value: "todo", label: "To Do" },
  { value: "in_progress", label: "In Progress" },
  { value: "review", label: "Review" },
  { value: "done", label: "Done" },
  { value: "cancelled", label: "Cancelled" },
];

export default function TaskListPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"list" | "kanban">("list");

  useEffect(() => {
    fetchTasksApi()
      .then(setTasks)
      .catch((err: Error) => setError(err.message || "Error loading tasks"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title="Tasks"
      actions={
        <button
          type="button"
          onClick={() => setView((v) => (v === "list" ? "kanban" : "list"))}
        >
          {view === "list" ? "Kanban" : "List"} view
        </button>
      }
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={tasks.length === 0}
      empty={{ title: "No tasks yet" }}
    >
      {view === "list" && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Project</th>
              <th>Assignee</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Due</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id}>
                <td>{t.name}</td>
                <td>{t.project_name}</td>
                <td>{t.assignee_name ?? "—"}</td>
                <td>{t.status}</td>
                <td>{t.priority}</td>
                <td>{t.due_date ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {view === "kanban" && (
        <div className="kanban-board">
          {STATUSES.map((s) => {
            const columnTasks = tasks.filter((t) => t.status === s.value);
            return (
              <div key={s.value} className="kanban-column">
                <h3>
                  {s.label} ({columnTasks.length})
                </h3>
                <ul>
                  {columnTasks.map((t) => (
                    <li key={t.id} className="kanban-card">
                      <strong>{t.name}</strong>
                      <div>{t.project_name}</div>
                      <div>{t.assignee_name ?? "—"}</div>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </ListPageShell>
  );
}
