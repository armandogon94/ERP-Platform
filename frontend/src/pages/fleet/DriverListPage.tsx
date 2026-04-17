import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type Driver, fetchDriversApi } from "../../api/fleet";

export default function DriverListPage() {
  const [rows, setRows] = useState<Driver[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const driverLabel = useTerminology("Driver", "Driver");

  useEffect(() => {
    fetchDriversApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading drivers"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{driverLabel}s</h1>

      <Link to="/fleet/drivers/new">New {driverLabel}</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>License #</th>
              <th>Expiry</th>
              <th>Phone</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((d) => (
              <tr key={d.id}>
                <td>
                  <Link to={`/fleet/drivers/${d.id}/edit`}>{d.name}</Link>
                </td>
                <td>{d.license_number}</td>
                <td>{d.license_expiry ?? "—"}</td>
                <td>{d.phone}</td>
                <td>{d.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
