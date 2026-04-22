import { useEffect, useState } from "react";
import { type MaintenanceLog, fetchMaintenanceLogsApi } from "../../api/fleet";
import ListPageShell from "../../components/ListPageShell";

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
    <ListPageShell
      title="Maintenance Logs"
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No maintenance logs yet" }}
    >
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
    </ListPageShell>
  );
}
