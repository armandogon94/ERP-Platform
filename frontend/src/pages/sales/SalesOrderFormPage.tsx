import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type SalesOrder,
  createSalesOrderApi,
  fetchSalesOrderApi,
  updateSalesOrderApi,
} from "../../api/sales";
import { type Partner, fetchPartnersApi } from "../../api/partners";

interface FormState {
  order_number: string;
  customer: string;
  customer_name: string;
  customer_email: string;
  status: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  order_number: "",
  customer: "",
  customer_name: "",
  customer_email: "",
  status: "confirmed",
  notes: "",
};

export default function SalesOrderFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const orderLabel = useTerminology("Sales Order", "Sales Order");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchPartnersApi({ is_customer: "true" })
      .then(setPartners)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchSalesOrderApi(Number(id))
      .then((so: SalesOrder) => {
        setForm({
          order_number: so.order_number,
          customer: so.customer != null ? String(so.customer) : "",
          customer_name: so.customer_name,
          customer_email: so.customer_email,
          status: so.status,
          notes: so.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading sales order");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => {
      if (name === "customer") {
        const partner = partners.find((p) => String(p.id) === value);
        return {
          ...prev,
          customer: value,
          customer_name: partner ? partner.name : prev.customer_name,
        };
      }
      return { ...prev, [name]: value };
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      customer: form.customer ? Number(form.customer) : null,
    };
    try {
      if (isEdit && id) {
        await updateSalesOrderApi(Number(id), payload);
      } else {
        await createSalesOrderApi(payload);
      }
      navigate("/sales/orders");
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
        {headingPrefix} {orderLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="order_number">Order Number</label>
          <input
            id="order_number"
            name="order_number"
            value={form.order_number}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="customer">Customer</label>
          <select
            id="customer"
            name="customer"
            value={form.customer}
            onChange={handleChange}
          >
            <option value="">-- Free text below --</option>
            {partners.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
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
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="confirmed">Confirmed</option>
            <option value="in_progress">In Progress</option>
            <option value="delivered">Delivered</option>
            <option value="invoiced">Invoiced</option>
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
