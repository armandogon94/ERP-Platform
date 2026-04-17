import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type Ticket,
  type TicketCategory,
  createTicketApi,
  fetchCategoriesApi,
  fetchTicketApi,
  reopenTicketApi,
  resolveTicketApi,
  updateTicketApi,
} from "../../api/helpdesk";

interface FormState {
  title: string;
  description: string;
  category: string;
  priority: string;
  status: string;
}

const EMPTY_FORM: FormState = {
  title: "",
  description: "",
  category: "",
  priority: "normal",
  status: "new",
};

export default function TicketFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [categories, setCategories] = useState<TicketCategory[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchCategoriesApi()
      .then(setCategories)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchTicketApi(Number(id))
      .then((t: Ticket) => {
        setForm({
          title: t.title,
          description: t.description,
          category: t.category != null ? String(t.category) : "",
          priority: t.priority,
          status: t.status,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading ticket");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      category: form.category ? Number(form.category) : null,
    };
    try {
      if (isEdit && id) {
        await updateTicketApi(Number(id), payload);
      } else {
        await createTicketApi(payload);
      }
      navigate("/helpdesk/tickets");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleResolve = async () => {
    if (!id) return;
    try {
      const t = await resolveTicketApi(Number(id));
      setForm((prev) => ({ ...prev, status: t.status }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Resolve failed");
    }
  };

  const handleReopen = async () => {
    if (!id) return;
    try {
      const t = await reopenTicketApi(Number(id));
      setForm((prev) => ({ ...prev, status: t.status }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reopen failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  const canResolve = !["resolved", "closed"].includes(form.status);
  const canReopen = ["resolved", "closed"].includes(form.status);

  return (
    <div>
      <h1>{headingPrefix} Ticket</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="category">Category</label>
          <select
            id="category"
            name="category"
            value={form.category}
            onChange={handleChange}
          >
            <option value="">-- None --</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            name="priority"
            value={form.priority}
            onChange={handleChange}
          >
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div>
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={form.status}
            onChange={handleChange}
          >
            <option value="new">New</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button type="submit">Save</button>
          {isEdit && canResolve && (
            <button type="button" onClick={handleResolve}>
              Resolve
            </button>
          )}
          {isEdit && canReopen && (
            <button type="button" onClick={handleReopen}>
              Reopen
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
