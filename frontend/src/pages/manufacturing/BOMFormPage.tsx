import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  type BOMLine,
  type BillOfMaterials,
  createBOMApi,
  createBOMLineApi,
  deleteBOMLineApi,
  fetchBOMApi,
  fetchBOMLinesApi,
  updateBOMApi,
} from "../../api/manufacturing";
import { type Product, fetchProductsApi } from "../../api/inventory";

interface FormState {
  product: string;
  version: string;
  active: boolean;
  notes: string;
}

const EMPTY_FORM: FormState = {
  product: "",
  version: "1.0",
  active: true,
  notes: "",
};

export default function BOMFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [lines, setLines] = useState<BOMLine[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [newComponent, setNewComponent] = useState("");
  const [newQty, setNewQty] = useState("1");
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchProductsApi()
      .then(setProducts)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchBOMApi(Number(id))
      .then((b: BillOfMaterials) => {
        setForm({
          product: String(b.product),
          version: b.version,
          active: b.active,
          notes: b.notes,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading BOM");
        setIsLoading(false);
      });
    fetchBOMLinesApi({ bom: String(id) })
      .then(setLines)
      .catch(() => {});
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
      product: Number(form.product) || null,
    };
    try {
      if (isEdit && id) {
        await updateBOMApi(Number(id), payload);
      } else {
        await createBOMApi(payload);
      }
      navigate("/manufacturing/boms");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  const handleAddLine = async () => {
    if (!id || !newComponent) return;
    try {
      const line = await createBOMLineApi({
        bom: Number(id),
        component: Number(newComponent),
        quantity: newQty,
      });
      setLines((prev) => [...prev, line]);
      setNewComponent("");
      setNewQty("1");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Add line failed");
    }
  };

  const handleDeleteLine = async (lineId: number) => {
    try {
      await deleteBOMLineApi(lineId);
      setLines((prev) => prev.filter((l) => l.id !== lineId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete line failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>{headingPrefix} BOM</h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="product">Product</label>
          <select
            id="product"
            name="product"
            value={form.product}
            onChange={handleChange}
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
          <label htmlFor="version">Version</label>
          <input
            id="version"
            name="version"
            value={form.version}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="active">
            <input
              id="active"
              name="active"
              type="checkbox"
              checked={form.active}
              onChange={handleChange}
            />{" "}
            Active
          </label>
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
        <>
          <h2 style={{ marginTop: "24px" }}>Components</h2>
          <table>
            <thead>
              <tr>
                <th>Component</th>
                <th>Quantity</th>
                <th>UoM</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lines.map((l) => (
                <tr key={l.id}>
                  <td>{l.component_name}</td>
                  <td>{l.quantity}</td>
                  <td>{l.uom}</td>
                  <td>
                    <button type="button" onClick={() => handleDeleteLine(l.id)}>
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div style={{ marginTop: "12px", display: "flex", gap: "8px" }}>
            <select
              value={newComponent}
              onChange={(e) => setNewComponent(e.target.value)}
            >
              <option value="">-- Select component --</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              min="0"
              step="0.01"
              value={newQty}
              onChange={(e) => setNewQty(e.target.value)}
              style={{ maxWidth: "120px" }}
            />
            <button type="button" onClick={handleAddLine}>
              Add component
            </button>
          </div>
        </>
      )}
    </div>
  );
}
