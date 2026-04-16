import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type PurchaseOrder,
  type Vendor,
  createPurchaseOrderApi,
  fetchPurchaseOrderApi,
  fetchVendorsApi,
  updatePurchaseOrderApi,
} from "../../api/purchasing";

interface FormState {
  vendor: string;
  po_number: string;
  status: string;
  notes: string;
}

const EMPTY_FORM: FormState = {
  vendor: "",
  po_number: "",
  status: "draft",
  notes: "",
};

export default function PurchaseOrderFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const poLabel = useTerminology("Purchase Order", "Purchase Order");
  const vendorLabel = useTerminology("Vendor", "Vendor");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchVendorsApi()
      .then(setVendors)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchPurchaseOrderApi(Number(id))
      .then((po: PurchaseOrder) => {
        setForm({
          vendor: String(po.vendor),
          po_number: po.po_number,
          status: po.status,
          notes: po.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading purchase order");
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
      vendor: Number(form.vendor) || undefined,
    };
    try {
      if (isEdit && id) {
        await updatePurchaseOrderApi(Number(id), payload);
      } else {
        await createPurchaseOrderApi(payload);
      }
      navigate("/purchasing/purchase-orders");
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
        {headingPrefix} {poLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="vendor">{vendorLabel}</label>
          <select id="vendor" name="vendor" value={form.vendor} onChange={handleChange}>
            <option value="">-- Select vendor --</option>
            {vendors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="po_number">PO Number</label>
          <input
            id="po_number"
            name="po_number"
            value={form.po_number}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="confirmed">Confirmed</option>
            <option value="received">Received</option>
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
