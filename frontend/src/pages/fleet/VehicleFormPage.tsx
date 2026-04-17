import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Driver,
  type Vehicle,
  createVehicleApi,
  fetchDriversApi,
  fetchVehicleApi,
  updateVehicleApi,
} from "../../api/fleet";

interface FormState {
  make: string;
  model: string;
  year: string;
  license_plate: string;
  vin: string;
  status: string;
  driver: string;
  mileage: string;
}

const EMPTY_FORM: FormState = {
  make: "",
  model: "",
  year: "2024",
  license_plate: "",
  vin: "",
  status: "active",
  driver: "",
  mileage: "0",
};

export default function VehicleFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const vehicleLabel = useTerminology("Vehicle", "Vehicle");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchDriversApi()
      .then(setDrivers)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;
    fetchVehicleApi(Number(id))
      .then((v: Vehicle) => {
        setForm({
          make: v.make,
          model: v.model,
          year: String(v.year),
          license_plate: v.license_plate,
          vin: v.vin,
          status: v.status,
          driver: v.driver != null ? String(v.driver) : "",
          mileage: String(v.mileage),
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading vehicle");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      year: Number(form.year) || 0,
      mileage: Number(form.mileage) || 0,
      driver: form.driver ? Number(form.driver) : null,
    };
    try {
      if (isEdit && id) {
        await updateVehicleApi(Number(id), payload);
      } else {
        await createVehicleApi(payload);
      }
      navigate("/fleet/vehicles");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>
        {headingPrefix} {vehicleLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="license_plate">License Plate</label>
          <input
            id="license_plate"
            name="license_plate"
            value={form.license_plate}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label htmlFor="make">Make</label>
          <input id="make" name="make" value={form.make} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="model">Model</label>
          <input id="model" name="model" value={form.model} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="year">Year</label>
          <input
            id="year"
            name="year"
            type="number"
            value={form.year}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="vin">VIN</label>
          <input id="vin" name="vin" value={form.vin} onChange={handleChange} />
        </div>
        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="active">Active</option>
            <option value="maintenance">In Maintenance</option>
            <option value="retired">Retired</option>
          </select>
        </div>
        <div>
          <label htmlFor="driver">Driver</label>
          <select id="driver" name="driver" value={form.driver} onChange={handleChange}>
            <option value="">-- Unassigned --</option>
            {drivers.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="mileage">Mileage</label>
          <input
            id="mileage"
            name="mileage"
            type="number"
            min="0"
            value={form.mileage}
            onChange={handleChange}
          />
        </div>
        <button type="submit">Save</button>
      </form>
    </div>
  );
}
