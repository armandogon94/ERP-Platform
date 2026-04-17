import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Driver,
  createDriverApi,
  fetchDriverApi,
  updateDriverApi,
} from "../../api/fleet";

interface FormState {
  name: string;
  license_number: string;
  license_expiry: string;
  phone: string;
  status: string;
}

const EMPTY_FORM: FormState = {
  name: "",
  license_number: "",
  license_expiry: "",
  phone: "",
  status: "active",
};

export default function DriverFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const driverLabel = useTerminology("Driver", "Driver");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchDriverApi(Number(id))
      .then((d: Driver) => {
        setForm({
          name: d.name,
          license_number: d.license_number,
          license_expiry: d.license_expiry ?? "",
          phone: d.phone,
          status: d.status,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading driver");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      license_expiry: form.license_expiry || null,
    };
    try {
      if (isEdit && id) {
        await updateDriverApi(Number(id), payload);
      } else {
        await createDriverApi(payload);
      }
      navigate("/fleet/drivers");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>
        {headingPrefix} {driverLabel}
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
          <label htmlFor="license_number">License Number</label>
          <input
            id="license_number"
            name="license_number"
            value={form.license_number}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="license_expiry">License Expiry</label>
          <input
            id="license_expiry"
            name="license_expiry"
            type="date"
            value={form.license_expiry}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="phone">Phone</label>
          <input id="phone" name="phone" value={form.phone} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={form.status}
            onChange={handleChange}
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
