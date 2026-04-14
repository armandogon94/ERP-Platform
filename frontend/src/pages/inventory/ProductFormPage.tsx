import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Product,
  createProductApi,
  fetchProductApi,
  updateProductApi,
} from "../../api/inventory";

interface FormState {
  name: string;
  sku: string;
  description: string;
  unit_of_measure: string;
  cost_price: string;
  sale_price: string;
  reorder_point: string;
  min_stock_level: string;
  is_active: boolean;
}

const EMPTY_FORM: FormState = {
  name: "",
  sku: "",
  description: "",
  unit_of_measure: "each",
  cost_price: "0.00",
  sale_price: "0.00",
  reorder_point: "",
  min_stock_level: "0.00",
  is_active: true,
};

export default function ProductFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const productLabel = useTerminology("Product", "Product");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchProductApi(Number(id))
      .then((p: Product) => {
        setForm({
          name: p.name,
          sku: p.sku,
          description: p.description,
          unit_of_measure: p.unit_of_measure,
          cost_price: p.cost_price,
          sale_price: p.sale_price,
          reorder_point: p.reorder_point ?? "",
          min_stock_level: p.min_stock_level,
          is_active: p.is_active,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading product");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>,
  ) => {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (isEdit && id) {
        await updateProductApi(Number(id), form);
      } else {
        await createProductApi(form);
      }
      navigate("/inventory/products");
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
        {headingPrefix} {productLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name</label>
          <input id="name" name="name" value={form.name} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="sku">SKU</label>
          <input id="sku" name="sku" value={form.sku} onChange={handleChange} />
        </div>

        <div>
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="unit_of_measure">Unit of Measure</label>
          <select
            id="unit_of_measure"
            name="unit_of_measure"
            value={form.unit_of_measure}
            onChange={handleChange}
          >
            <option value="each">Each</option>
            <option value="box">Box</option>
            <option value="case">Case</option>
            <option value="kg">Kilogram</option>
            <option value="liter">Liter</option>
            <option value="meter">Meter</option>
          </select>
        </div>

        <div>
          <label htmlFor="cost_price">Cost Price</label>
          <input
            id="cost_price"
            name="cost_price"
            type="number"
            step="0.01"
            value={form.cost_price}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="sale_price">Sale Price</label>
          <input
            id="sale_price"
            name="sale_price"
            type="number"
            step="0.01"
            value={form.sale_price}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="reorder_point">Reorder Point</label>
          <input
            id="reorder_point"
            name="reorder_point"
            type="number"
            step="0.01"
            value={form.reorder_point}
            onChange={handleChange}
          />
        </div>

        <button type="submit">Save</button>
      </form>
    </div>
  );
}
