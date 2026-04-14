import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type JournalEntry, fetchJournalEntriesApi } from "../../api/accounting";

export default function JournalEntryListPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchJournalEntriesApi()
      .then(setEntries)
      .catch((err: Error) => setError(err.message || "Error loading journal entries"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Journal Entries</h1>

      <Link to="/accounting/entries/new">New Journal Entry</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Reference</th>
              <th>Journal</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.id}>
                <td>
                  <Link to={`/accounting/entries/${e.id}/edit`}>{e.reference}</Link>
                </td>
                <td>{e.journal_name}</td>
                <td>{e.entry_date ?? "—"}</td>
                <td>{e.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
