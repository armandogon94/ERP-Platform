import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type POSOrder,
  type POSSession,
  createPOSOrderApi,
  fetchPOSOrderApi,
  fetchPOSSessionsApi,
  updatePOSOrderApi,
} from "../../api/pos";
import { type Partner, fetchPartnersApi } from "../../api/partners";

interface FormState {
  session: string;
  customer: string;
  subtotal: string;
  tax_amount: string;
  total: string;
  status: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  session: "",
  customer: "",
  subtotal: "0",
  tax_amount: "0",
  total: "0",
  status: "draft",
  notes: "",
};

export default function POSOrderFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [sessions, setSessions] = useState<POSSession[]>([]);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchPOSSessionsApi({ status: "open" })
      .then(setSessions)
      .catch(() => {});
    fetchPartnersApi({ is_customer: "true" })
      .then(setPartners)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchPOSOrderApi(Number(id))
      .then((o: POSOrder) => {
        setForm({
          session: String(o.session),
          customer: o.customer != null ? String(o.customer) : "",
          subtotal: o.subtotal,
          tax_amount: o.tax_amount,
          total: o.total,
          status: o.status,
          notes: o.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading order");
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
      session: Number(form.session) || null,
      customer: form.customer ? Number(form.customer) : null,
    };
    try {
      if (isEdit && id) {
        await updatePOSOrderApi(Number(id), payload);
      } else {
        await createPOSOrderApi(payload);
      }
      navigate("/pos/orders");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{headingPrefix} Order</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="session">Session</label>
          <select
            id="session"
            name="session"
            value={form.session}
            onChange={handleChange}
          >
            <option value="">-- Select session --</option>
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                {s.station} — {s.status}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="customer">Customer</label>
          <select
            id="customer"
            name="customer"
            value={form.customer}
            onChange={handleChange}
          >
            <option value="">-- Walk-in / none --</option>
            {partners.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="subtotal">Subtotal</label>
          <input
            id="subtotal"
            name="subtotal"
            type="number"
            min="0"
            step="0.01"
            value={form.subtotal}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="tax_amount">Tax</label>
          <input
            id="tax_amount"
            name="tax_amount"
            type="number"
            min="0"
            step="0.01"
            value={form.tax_amount}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="total">Total</label>
          <input
            id="total"
            name="total"
            type="number"
            min="0"
            step="0.01"
            value={form.total}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="paid">Paid</option>
            <option value="refunded">Refunded</option>
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
