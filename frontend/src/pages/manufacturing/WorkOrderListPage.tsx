import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type WorkOrder, fetchWorkOrdersApi } from "../../api/manufacturing";

export default function WorkOrderListPage() {
  const [rows, setRows] = useState<WorkOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchWorkOrdersApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading work orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Work Orders</h1>

      <Link to="/manufacturing/work-orders/new">New Work Order</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Target</th>
              <th>Done</th>
              <th>Status</th>
              <th>Start</th>
              <th>End</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((w) => (
              <tr key={w.id}>
                <td>
                  <Link to={`/manufacturing/work-orders/${w.id}/edit`}>
                    {w.product_name}
                  </Link>
                </td>
                <td>{w.quantity_target}</td>
                <td>{w.quantity_done}</td>
                <td>{w.status}</td>
                <td>{w.start_date ?? "—"}</td>
                <td>{w.end_date ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
