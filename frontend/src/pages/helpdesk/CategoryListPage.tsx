import { useEffect, useState } from "react";
import ListPageShell from "../../components/ListPageShell";
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
    <ListPageShell
      title="Ticket Categories"
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No ticket categories yet" }}
    >
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
    </ListPageShell>
  );
}
