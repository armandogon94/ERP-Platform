import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type Invoice,
  createInvoiceApi,
  fetchInvoiceApi,
  updateInvoiceApi,
} from "../../api/invoicing";

interface FormState {
  invoice_number: string;
  invoice_type: string;
  status: string;
  customer_name: string;
  customer_email: string;
  invoice_date: string;
  due_date: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  invoice_number: "",
  invoice_type: "customer",
  status: "draft",
  customer_name: "",
  customer_email: "",
  invoice_date: "",
  due_date: "",
  notes: "",
};

export default function InvoiceFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchInvoiceApi(Number(id))
      .then((inv: Invoice) => {
        setForm({
          invoice_number: inv.invoice_number,
          invoice_type: inv.invoice_type,
          status: inv.status,
          customer_name: inv.customer_name,
          customer_email: inv.customer_email,
          invoice_date: inv.invoice_date ?? "",
          due_date: inv.due_date ?? "",
          notes: inv.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading invoice");
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
      invoice_date: form.invoice_date || null,
      due_date: form.due_date || null,
    };
    try {
      if (isEdit && id) {
        await updateInvoiceApi(Number(id), payload);
      } else {
        await createInvoiceApi(payload);
      }
      navigate("/invoicing/invoices");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>{headingPrefix} Invoice</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="invoice_number">Invoice Number</label>
          <input
            id="invoice_number"
            name="invoice_number"
            value={form.invoice_number}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="invoice_type">Invoice Type</label>
          <select
            id="invoice_type"
            name="invoice_type"
            value={form.invoice_type}
            onChange={handleChange}
          >
            <option value="customer">Customer Invoice</option>
            <option value="vendor">Vendor Bill</option>
          </select>
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="posted">Posted</option>
            <option value="paid">Paid</option>
            <option value="cancelled">Cancelled</option>
          </select>
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
          <label htmlFor="invoice_date">Invoice Date</label>
          <input
            id="invoice_date"
            name="invoice_date"
            type="date"
            value={form.invoice_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="due_date">Due Date</label>
          <input
            id="due_date"
            name="due_date"
            type="date"
            value={form.due_date}
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
