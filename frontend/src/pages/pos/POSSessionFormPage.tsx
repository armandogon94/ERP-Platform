import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type POSSession,
  closePOSSessionApi,
  createPOSSessionApi,
  fetchPOSSessionApi,
  updatePOSSessionApi,
} from "../../api/pos";

interface FormState {
  station: string;
  cash_on_open: string;
  cash_on_close: string;
  notes: string;
  status: string;
  expected_cash: string;
  variance: string;
}

const EMPTY_FORM: FormState = {
  station: "",
  cash_on_open: "0",
  cash_on_close: "",
  notes: "",
  status: "open",
  expected_cash: "",
  variance: "",
};

export default function POSSessionFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchPOSSessionApi(Number(id))
      .then((s: POSSession) => {
        setForm({
          station: s.station,
          cash_on_open: s.cash_on_open,
          cash_on_close: s.cash_on_close ?? "",
          notes: s.notes,
          status: s.status,
          expected_cash: s.expected_cash ?? "",
          variance: s.variance ?? "",
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading session");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      station: form.station,
      cash_on_open: form.cash_on_open,
      notes: form.notes,
    };
    try {
      if (isEdit && id) {
        await updatePOSSessionApi(Number(id), payload);
      } else {
        await createPOSSessionApi(payload);
      }
      navigate("/pos/sessions");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleClose = async () => {
    if (!id || !form.cash_on_close) {
      setError("Enter cash-on-close before closing the session.");
      return;
    }
    try {
      const updated = await closePOSSessionApi(Number(id), {
        cash_on_close: form.cash_on_close,
      });
      setForm((prev) => ({
        ...prev,
        status: updated.status,
        expected_cash: updated.expected_cash ?? "",
        variance: updated.variance ?? "",
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Close failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  const canClose = form.status === "open";

  return (
    <div>
      <h1>{headingPrefix} Session</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="station">Station</label>
          <input
            id="station"
            name="station"
            value={form.station}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="cash_on_open">Cash on Open</label>
          <input
            id="cash_on_open"
            name="cash_on_open"
            type="number"
            min="0"
            step="0.01"
            value={form.cash_on_open}
            onChange={handleChange}
          />
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

      {isEdit && (
        <div style={{ marginTop: "24px" }}>
          <h2>Close Session</h2>
          <div>
            <label htmlFor="cash_on_close">Cash on Close</label>
            <input
              id="cash_on_close"
              name="cash_on_close"
              type="number"
              min="0"
              step="0.01"
              value={form.cash_on_close}
              onChange={handleChange}
              disabled={!canClose}
            />
          </div>
          {form.expected_cash && (
            <div>Expected: {form.expected_cash}</div>
          )}
          {form.variance && (
            <div>Variance: {form.variance}</div>
          )}
          <button
            type="button"
            onClick={handleClose}
            disabled={!canClose}
            style={{ marginTop: "8px" }}
          >
            Close Session
          </button>
        </div>
      )}
    </div>
  );
}
