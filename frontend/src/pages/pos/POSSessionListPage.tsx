import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { type POSSession, fetchPOSSessionsApi } from "../../api/pos";

export default function POSSessionListPage() {
  const [rows, setRows] = useState<POSSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPOSSessionsApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading sessions"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title="POS Sessions"
      actions={<Link to="/pos/sessions/new">New Session</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No POS sessions yet" }}
    >
      <table>
        <thead>
          <tr>
            <th>Station</th>
            <th>Opened By</th>
            <th>Opened At</th>
            <th>Cash on Open</th>
            <th>Cash on Close</th>
            <th>Variance</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((s) => (
            <tr key={s.id}>
              <td>
                <Link to={`/pos/sessions/${s.id}/edit`}>{s.station}</Link>
              </td>
              <td>{s.opened_by_username}</td>
              <td>{new Date(s.opened_at).toLocaleString()}</td>
              <td>{s.cash_on_open}</td>
              <td>{s.cash_on_close ?? "—"}</td>
              <td>{s.variance ?? "—"}</td>
              <td>{s.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
