import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
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
    <ListPageShell
      title={`${driverLabel}s`}
      actions={<Link to="/fleet/drivers/new">New {driverLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: `No ${driverLabel.toLowerCase()}s yet` }}
    >
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
    </ListPageShell>
  );
}
