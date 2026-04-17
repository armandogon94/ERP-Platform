import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type JournalEntry, fetchJournalEntriesApi } from "../../api/accounting";
import Skeleton from "../../components/Skeleton";

export default function JournalEntryListPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const entryLabel = useTerminology("Journal Entry", "Journal Entry");

  useEffect(() => {
    fetchJournalEntriesApi()
      .then(setEntries)
      .catch((err: Error) => setError(err.message || "Error loading journal entries"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{entryLabel === "Journal Entry" ? "Journal Entries" : `${entryLabel}s`}</h1>

      <Link to="/accounting/entries/new">New {entryLabel}</Link>

      {isLoading && <Skeleton />}
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
