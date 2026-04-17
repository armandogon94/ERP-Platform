import { useEffect, useState } from "react";
import { type MaintenanceLog, fetchMaintenanceLogsApi } from "../../api/fleet";
import Skeleton from "../../components/Skeleton";

export default function MaintenanceLogListPage() {
  const [rows, setRows] = useState<MaintenanceLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMaintenanceLogsApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading maintenance logs"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Maintenance Logs</h1>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Vehicle</th>
              <th>Date</th>
              <th>Description</th>
              <th>Mechanic</th>
              <th>Cost</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m) => (
              <tr key={m.id}>
                <td>{m.vehicle_plate}</td>
                <td>{m.date ?? "—"}</td>
                <td>{m.description}</td>
                <td>{m.mechanic}</td>
                <td>{m.cost}</td>
                <td>{m.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
