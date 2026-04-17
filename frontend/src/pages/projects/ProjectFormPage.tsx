import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Project,
  createProjectApi,
  fetchProjectApi,
  updateProjectApi,
} from "../../api/projects";
import { type Partner, fetchPartnersApi } from "../../api/partners";

interface FormState {
  name: string;
  code: string;
  customer: string;
  status: string;
  start_date: string;
  end_date: string;
  budget: string;
  description: string;
}

const EMPTY_FORM: FormState = {
  name: "",
  code: "",
  customer: "",
  status: "planned",
  start_date: "",
  end_date: "",
  budget: "0",
  description: "",
};

export default function ProjectFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const projectLabel = useTerminology("Project", "Project");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchPartnersApi({ is_customer: "true" })
      .then(setPartners)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchProjectApi(Number(id))
      .then((p: Project) => {
        setForm({
          name: p.name,
          code: p.code,
          customer: p.customer != null ? String(p.customer) : "",
          status: p.status,
          start_date: p.start_date ?? "",
          end_date: p.end_date ?? "",
          budget: p.budget,
          description: p.description,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading project");
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
      customer: form.customer ? Number(form.customer) : null,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
    };
    try {
      if (isEdit && id) {
        await updateProjectApi(Number(id), payload);
      } else {
        await createProjectApi(payload);
      }
      navigate("/projects/projects");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>
        {headingPrefix} {projectLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name</label>
          <input
            id="name"
            name="name"
            value={form.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="code">Code</label>
          <input id="code" name="code" value={form.code} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="customer">Customer</label>
          <select
            id="customer"
            name="customer"
            value={form.customer}
            onChange={handleChange}
          >
            <option value="">-- Internal / none --</option>
            {partners.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
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
            <option value="planned">Planned</option>
            <option value="active">Active</option>
            <option value="on_hold">On Hold</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div>
          <label htmlFor="start_date">Start Date</label>
          <input
            id="start_date"
            name="start_date"
            type="date"
            value={form.start_date}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="end_date">End Date</label>
          <input
            id="end_date"
            name="end_date"
            type="date"
            value={form.end_date}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="budget">Budget</label>
          <input
            id="budget"
            name="budget"
            type="number"
            min="0"
            step="0.01"
            value={form.budget}
            onChange={handleChange}
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
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
