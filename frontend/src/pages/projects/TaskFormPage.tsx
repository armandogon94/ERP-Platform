import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Project,
  type Task,
  createTaskApi,
  fetchProjectsApi,
  fetchTaskApi,
  updateTaskApi,
} from "../../api/projects";

interface FormState {
  name: string;
  project: string;
  status: string;
  priority: string;
  due_date: string;
  description: string;
}

const EMPTY: FormState = {
  name: "",
  project: "",
  status: "todo",
  priority: "normal",
  due_date: "",
  description: "",
};

/** REVIEW S-10: form page for Task. Milestone + Category remain inline-only. */
export default function TaskFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const taskLabel = useTerminology("Task", "Task");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchProjectsApi().then(setProjects).catch(() => {});
    if (isEdit && id) {
      fetchTaskApi(Number(id))
        .then((t: Task) =>
          setForm({
            name: t.name,
            project: String(t.project),
            status: t.status,
            priority: t.priority,
            due_date: t.due_date ?? "",
            description: t.description,
          }),
        )
        .catch((e: Error) => setError(e.message || "Failed to load"))
        .finally(() => setIsLoading(false));
    }
  }, [id, isEdit]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const payload: Partial<Task> = {
      name: form.name,
      project: Number(form.project),
      status: form.status,
      priority: form.priority,
      due_date: form.due_date || null,
      description: form.description,
    };
    try {
      if (isEdit && id) {
        await updateTaskApi(Number(id), payload);
      } else {
        await createTaskApi(payload);
      }
      navigate("/projects/tasks");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  if (isLoading) return <div role="status">Loading…</div>;

  return (
    <div>
      <h1>
        {headingPrefix} {taskLabel}
      </h1>
      {error && <div role="alert">{error}</div>}
      <form onSubmit={onSubmit}>
        <label>
          Name
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>
        <label>
          Project
          <select
            value={form.project}
            onChange={(e) => setForm({ ...form, project: e.target.value })}
            required
          >
            <option value="">—</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value })}
          >
            <option value="todo">Todo</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </label>
        <label>
          Priority
          <select
            value={form.priority}
            onChange={(e) => setForm({ ...form, priority: e.target.value })}
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </label>
        <label>
          Due Date
          <input
            type="date"
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
          />
        </label>
        <label>
          Description
          <textarea
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
