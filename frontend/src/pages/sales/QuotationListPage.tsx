import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type SalesQuotation, fetchQuotationsApi } from "../../api/sales";

export default function QuotationListPage() {
  const [quotations, setQuotations] = useState<SalesQuotation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchQuotationsApi()
      .then(setQuotations)
      .catch((err: Error) => setError(err.message || "Error loading quotations"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Quotations</h1>

      <Link to="/sales/quotations/new">New Quotation</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
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
      )}
    </div>
  );
}
