import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Partner,
  createPartnerApi,
  fetchPartnerApi,
  updatePartnerApi,
} from "../../api/partners";

interface FormState {
  name: string;
  email: string;
  phone: string;
  is_customer: boolean;
  is_vendor: boolean;
  tax_id: string;
  payment_terms_days: string;
  credit_limit: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  name: "",
  email: "",
  phone: "",
  is_customer: true,
  is_vendor: false,
  tax_id: "",
  payment_terms_days: "0",
  credit_limit: "0",
  notes: "",
};

export default function PartnerFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const partnerLabel = useTerminology("Partner", "Partner");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchPartnerApi(Number(id))
      .then((p: Partner) => {
        setForm({
          name: p.name,
          email: p.email,
          phone: p.phone,
          is_customer: p.is_customer,
          is_vendor: p.is_vendor,
          tax_id: p.tax_id,
          payment_terms_days: String(p.payment_terms_days),
          credit_limit: p.credit_limit,
          notes: p.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading partner");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, checked } = target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      payment_terms_days: Number(form.payment_terms_days) || 0,
    };
    try {
      if (isEdit && id) {
        await updatePartnerApi(Number(id), payload);
      } else {
        await createPartnerApi(payload);
      }
      navigate("/partners");
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
        {headingPrefix} {partnerLabel}
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
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="phone">Phone</label>
          <input id="phone" name="phone" value={form.phone} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="is_customer">
            <input
              id="is_customer"
              name="is_customer"
              type="checkbox"
              checked={form.is_customer}
              onChange={handleChange}
            />{" "}
            Customer
          </label>
        </div>

        <div>
          <label htmlFor="is_vendor">
            <input
              id="is_vendor"
              name="is_vendor"
              type="checkbox"
              checked={form.is_vendor}
              onChange={handleChange}
            />{" "}
            Vendor
          </label>
        </div>

        <div>
          <label htmlFor="tax_id">Tax ID</label>
          <input
            id="tax_id"
            name="tax_id"
            value={form.tax_id}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="payment_terms_days">Payment Terms (days)</label>
          <input
            id="payment_terms_days"
            name="payment_terms_days"
            type="number"
            min="0"
            value={form.payment_terms_days}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="credit_limit">Credit Limit</label>
          <input
            id="credit_limit"
            name="credit_limit"
            type="number"
            min="0"
            step="0.01"
            value={form.credit_limit}
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
    </div>
  );
}
