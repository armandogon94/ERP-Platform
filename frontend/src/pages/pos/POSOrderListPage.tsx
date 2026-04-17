import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type POSOrder, fetchPOSOrdersApi } from "../../api/pos";

export default function POSOrderListPage() {
  const [rows, setRows] = useState<POSOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPOSOrdersApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>POS Orders</h1>

      <Link to="/pos/orders/new">New Order</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Order #</th>
              <th>Customer</th>
              <th>Subtotal</th>
              <th>Tax</th>
              <th>Total</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((o) => (
              <tr key={o.id}>
                <td>
                  <Link to={`/pos/orders/${o.id}/edit`}>{o.order_number}</Link>
                </td>
                <td>{o.customer_name ?? "—"}</td>
                <td>{o.subtotal}</td>
                <td>{o.tax_amount}</td>
                <td>{o.total}</td>
                <td>{o.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
