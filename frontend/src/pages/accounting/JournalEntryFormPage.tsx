import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Journal,
  type JournalEntry,
  createJournalEntryApi,
  fetchJournalEntryApi,
  fetchJournalsApi,
  updateJournalEntryApi,
} from "../../api/accounting";

interface FormState {
  journal: string;
  reference: string;
  entry_date: string;
  status: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  journal: "",
  reference: "",
  entry_date: "",
  status: "draft",
  notes: "",
};

export default function JournalEntryFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [journals, setJournals] = useState<Journal[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const entryLabel = useTerminology("Journal Entry", "Journal Entry");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchJournalsApi()
      .then(setJournals)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchJournalEntryApi(Number(id))
      .then((entry: JournalEntry) => {
        setForm({
          journal: String(entry.journal),
          reference: entry.reference,
          entry_date: entry.entry_date ?? "",
          status: entry.status,
          notes: entry.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading journal entry");
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
      journal: Number(form.journal) || undefined,
      entry_date: form.entry_date || null,
    };
    try {
      if (isEdit && id) {
        await updateJournalEntryApi(Number(id), payload);
      } else {
        await createJournalEntryApi(payload);
      }
      navigate("/accounting/entries");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>
        {headingPrefix} {entryLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="journal">Journal</label>
          <select
            id="journal"
            name="journal"
            value={form.journal}
            onChange={handleChange}
          >
            <option value="">-- Select journal --</option>
            {journals.map((j) => (
              <option key={j.id} value={j.id}>
                {j.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="reference">Reference</label>
          <input
            id="reference"
            name="reference"
            value={form.reference}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="entry_date">Entry Date</label>
          <input
            id="entry_date"
            name="entry_date"
            type="date"
            value={form.entry_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="posted">Posted</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <div>
          <label htmlFor="notes">Notes</label>
          <textarea
            id="notes"
            name="notes"
            value={form.notes}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Save</button>
      </form>
    </div>
  );
}
