import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type SalesOrder, fetchSalesOrdersApi } from "../../api/sales";

export default function SalesOrderListPage() {
  const [orders, setOrders] = useState<SalesOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const orderLabel = useTerminology("Sales Order", "Sales Order");

  useEffect(() => {
    fetchSalesOrdersApi()
      .then(setOrders)
      .catch((err: Error) => setError(err.message || "Error loading sales orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title={`${orderLabel}s`}
      actions={<Link to="/sales/orders/new">New {orderLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={orders.length === 0}
      empty={{ title: `No ${orderLabel.toLowerCase()}s yet` }}
    >
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
    </ListPageShell>
  );
}
