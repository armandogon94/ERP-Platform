import { useEffect, useState } from "react";
import { type FuelLog, fetchFuelLogsApi } from "../../api/fleet";
import ListPageShell from "../../components/ListPageShell";

export default function FuelLogListPage() {
  const [rows, setRows] = useState<FuelLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFuelLogsApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading fuel logs"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title="Fuel Logs"
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No fuel logs yet" }}
    >
      <table>
        <thead>
          <tr>
            <th>Vehicle</th>
            <th>Date</th>
            <th>Liters</th>
            <th>Cost / L</th>
            <th>Total</th>
            <th>Mileage</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((f) => (
            <tr key={f.id}>
              <td>{f.vehicle_plate}</td>
              <td>{f.date ?? "—"}</td>
              <td>{f.liters}</td>
              <td>{f.cost_per_liter}</td>
              <td>{f.total_cost}</td>
              <td>{f.mileage_at_fill}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
