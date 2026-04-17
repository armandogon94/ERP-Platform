import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type Vehicle, fetchVehiclesApi } from "../../api/fleet";
import Skeleton from "../../components/Skeleton";

export default function VehicleListPage() {
  const [rows, setRows] = useState<Vehicle[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const vehicleLabel = useTerminology("Vehicle", "Vehicle");

  useEffect(() => {
    fetchVehiclesApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading vehicles"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{vehicleLabel}s</h1>

      <Link to="/fleet/vehicles/new">New {vehicleLabel}</Link>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Plate</th>
              <th>Make / Model</th>
              <th>Year</th>
              <th>Status</th>
              <th>Driver</th>
              <th>Mileage</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((v) => (
              <tr key={v.id}>
                <td>
                  <Link to={`/fleet/vehicles/${v.id}/edit`}>{v.license_plate}</Link>
                </td>
                <td>
                  {v.make} {v.model}
                </td>
                <td>{v.year}</td>
                <td>{v.status}</td>
                <td>{v.driver_name ?? "—"}</td>
                <td>{v.mileage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
