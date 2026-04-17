import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type BillOfMaterials,
  type WorkOrder,
  completeWorkOrderApi,
  createWorkOrderApi,
  fetchBOMsApi,
  fetchWorkOrderApi,
  startWorkOrderApi,
  updateWorkOrderApi,
} from "../../api/manufacturing";
import { type Product, fetchProductsApi } from "../../api/inventory";

interface FormState {
  product: string;
  bom: string;
  quantity_target: string;
  status: string;
  start_date: string;
  end_date: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  product: "",
  bom: "",
  quantity_target: "1",
  status: "draft",
  start_date: "",
  end_date: "",
  notes: "",
};

export default function WorkOrderFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [products, setProducts] = useState<Product[]>([]);
  const [boms, setBOMs] = useState<BillOfMaterials[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchProductsApi()
      .then(setProducts)
      .catch(() => {});
    fetchBOMsApi()
      .then(setBOMs)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchWorkOrderApi(Number(id))
      .then((w: WorkOrder) => {
        setForm({
          product: String(w.product),
          bom: w.bom != null ? String(w.bom) : "",
          quantity_target: w.quantity_target,
          status: w.status,
          start_date: w.start_date ?? "",
          end_date: w.end_date ?? "",
          notes: w.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading work order");
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
      product: Number(form.product) || null,
      bom: form.bom ? Number(form.bom) : null,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
    };
    try {
      if (isEdit && id) {
        await updateWorkOrderApi(Number(id), payload);
      } else {
        await createWorkOrderApi(payload);
      }
      navigate("/manufacturing/work-orders");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleStart = async () => {
    if (!id) return;
    try {
      const wo = await startWorkOrderApi(Number(id));
      setForm((prev) => ({ ...prev, status: wo.status }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Start failed");
    }
  };

  const handleComplete = async () => {
    if (!id) return;
    try {
      const wo = await completeWorkOrderApi(Number(id));
      setForm((prev) => ({ ...prev, status: wo.status }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Complete failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  const canStart = ["draft", "confirmed"].includes(form.status);
  const canComplete = form.status === "in_progress";

  return (
    <div>
      <h1>{headingPrefix} Work Order</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="product">Product</label>
          <select
            id="product"
            name="product"
            value={form.product}
            onChange={handleChange}
            required
          >
            <option value="">-- Select product --</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="bom">Bill of Materials</label>
          <select id="bom" name="bom" value={form.bom} onChange={handleChange}>
            <option value="">-- None --</option>
            {boms.map((b) => (
              <option key={b.id} value={b.id}>
                {b.product_name} v{b.version}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="quantity_target">Quantity Target</label>
          <input
            id="quantity_target"
            name="quantity_target"
            type="number"
            min="0"
            step="0.01"
            value={form.quantity_target}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="confirmed">Confirmed</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
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
          <label htmlFor="notes">Notes</label>
          <textarea
            id="notes"
            name="notes"
            value={form.notes}
            onChange={handleChange}
          />
        </div>
        <div style={{ display: "flex", gap: "8px" }}>
          <button type="submit">Save</button>
          {isEdit && canStart && (
            <button type="button" onClick={handleStart}>
              Start
            </button>
          )}
          {isEdit && canComplete && (
            <button type="button" onClick={handleComplete}>
              Complete
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
