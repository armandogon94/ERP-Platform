import { useEffect, useState } from "react";
import { type TicketCategory, fetchCategoriesApi } from "../../api/helpdesk";

export default function CategoryListPage() {
  const [rows, setRows] = useState<TicketCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCategoriesApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading categories"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Ticket Categories</h1>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>SLA Hours</th>
              <th>Industry Tag</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.sla_hours}</td>
                <td>{c.industry_tag}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
