import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type PurchaseOrder, fetchPurchaseOrdersApi } from "../../api/purchasing";

export default function PurchaseOrderListPage() {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const poLabel = useTerminology("Purchase Order", "Purchase Order");

  useEffect(() => {
    fetchPurchaseOrdersApi()
      .then(setOrders)
      .catch((err: Error) => setError(err.message || "Error loading purchase orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{poLabel}s</h1>

      <Link to="/purchasing/purchase-orders/new">New {poLabel}</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>PO Number</th>
              <th>Vendor</th>
              <th>Status</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((po) => (
              <tr key={po.id}>
                <td>
                  <Link to={`/purchasing/purchase-orders/${po.id}/edit`}>
                    {po.po_number}
                  </Link>
                </td>
                <td>{po.vendor_name}</td>
                <td>{po.status}</td>
                <td>{po.total_amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
