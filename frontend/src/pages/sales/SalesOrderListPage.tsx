import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type SalesOrder, fetchSalesOrdersApi } from "../../api/sales";

export default function SalesOrderListPage() {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSalesOrdersApi()
      .then(setOrders)
      .catch((err: Error) => setError(err.message || "Error loading sales orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Sales Orders</h1>

      <Link to="/sales/orders/new">New Sales Order</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Order Number</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((so) => (
              <tr key={so.id}>
                <td>
                  <Link to={`/sales/orders/${so.id}/edit`}>{so.order_number}</Link>
                </td>
                <td>{so.customer_name}</td>
                <td>{so.status}</td>
                <td>{so.total_amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
