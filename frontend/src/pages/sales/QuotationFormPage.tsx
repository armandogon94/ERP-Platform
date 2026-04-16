import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type SalesQuotation,
  createQuotationApi,
  fetchQuotationApi,
  updateQuotationApi,
} from "../../api/sales";

interface FormState {
  quotation_number: string;
  customer_name: string;
  customer_email: string;
  status: string;
  valid_until: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  quotation_number: "",
  customer_name: "",
  customer_email: "",
  status: "draft",
  valid_until: "",
  notes: "",
};

export default function QuotationFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const quotationLabel = useTerminology("Quotation", "Quotation");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchQuotationApi(Number(id))
      .then((q: SalesQuotation) => {
        setForm({
          quotation_number: q.quotation_number,
          customer_name: q.customer_name,
          customer_email: q.customer_email,
          status: q.status,
          valid_until: q.valid_until ?? "",
          notes: q.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading quotation");
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
      valid_until: form.valid_until || null,
    };
    try {
      if (isEdit && id) {
        await updateQuotationApi(Number(id), payload);
      } else {
        await createQuotationApi(payload);
      }
      navigate("/sales/quotations");
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
        {headingPrefix} {quotationLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="quotation_number">{quotationLabel} Number</label>
          <input
            id="quotation_number"
            name="quotation_number"
            value={form.quotation_number}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="customer_name">Customer Name</label>
          <input
            id="customer_name"
            name="customer_name"
            value={form.customer_name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="customer_email">Customer Email</label>
          <input
            id="customer_email"
            name="customer_email"
            type="email"
            value={form.customer_email}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="accepted">Accepted</option>
            <option value="declined">Declined</option>
            <option value="expired">Expired</option>
          </select>
        </div>

        <div>
          <label htmlFor="valid_until">Valid Until</label>
          <input
            id="valid_until"
            name="valid_until"
            type="date"
            value={form.valid_until}
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
