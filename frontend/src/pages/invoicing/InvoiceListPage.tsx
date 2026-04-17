import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type Invoice, fetchInvoicesApi } from "../../api/invoicing";
import Skeleton from "../../components/Skeleton";

export default function InvoiceListPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const invoiceLabel = useTerminology("Invoice", "Invoice");

  useEffect(() => {
    fetchInvoicesApi()
      .then(setInvoices)
      .catch((err: Error) => setError(err.message || "Error loading invoices"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{invoiceLabel}s</h1>

      <Link to="/invoicing/invoices/new">New {invoiceLabel}</Link>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Invoice Number</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id}>
                <td>
                  <Link to={`/invoicing/invoices/${inv.id}/edit`}>
                    {inv.invoice_number}
                  </Link>
                </td>
                <td>{inv.customer_name}</td>
                <td>{inv.status}</td>
                <td>{inv.total_amount}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
