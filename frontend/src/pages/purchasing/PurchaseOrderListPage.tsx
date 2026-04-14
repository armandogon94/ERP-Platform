import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type PurchaseOrder, fetchPurchaseOrdersApi } from "../../api/purchasing";

export default function PurchaseOrderListPage() {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPurchaseOrdersApi()
      .then(setOrders)
      .catch((err: Error) => setError(err.message || "Error loading purchase orders"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Purchase Orders</h1>

      <Link to="/purchasing/purchase-orders/new">New Purchase Order</Link>

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
