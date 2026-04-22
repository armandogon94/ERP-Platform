import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type SalesQuotation, fetchQuotationsApi } from "../../api/sales";

export default function QuotationListPage() {
  const [quotations, setQuotations] = useState<SalesQuotation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const quotationLabel = useTerminology("Quotation", "Quotation");

  useEffect(() => {
    fetchQuotationsApi()
      .then(setQuotations)
      .catch((err: Error) => setError(err.message || "Error loading quotations"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title={`${quotationLabel}s`}
      actions={<Link to="/sales/quotations/new">New {quotationLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={quotations.length === 0}
      empty={{ title: `No ${quotationLabel.toLowerCase()}s yet` }}
    >
      <table>
        <thead>
          <tr>
            <th>Number</th>
            <th>Customer</th>
            <th>Status</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {quotations.map((q) => (
            <tr key={q.id}>
              <td>
                <Link to={`/sales/quotations/${q.id}/edit`}>
                  {q.quotation_number}
                </Link>
              </td>
              <td>{q.customer_name}</td>
              <td>{q.status}</td>
              <td>{q.total_amount}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
