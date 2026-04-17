import { useEffect, useState } from "react";
import EmptyState from "../../components/EmptyState";
import Skeleton from "../../components/Skeleton";
import { fetchAuditLogApi, type AuditLogEntry } from "../../api/auditLog";

function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function AuditLogTimelinePage(): JSX.Element {
  const [entries, setEntries] = useState<AuditLogEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchAuditLogApi()
      .then((res) => {
        if (!cancelled) setEntries(res);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="audit-log-page">
      <h1>Audit Log</h1>

      {error && <div role="alert">Error: {error}</div>}
      {entries === null && <Skeleton lines={6} />}

      {entries !== null && entries.length === 0 && (
        <EmptyState
          title="No audit entries yet"
          description="Every create/update action on company records will appear here."
        />
      )}

      {entries !== null && entries.length > 0 && (
        <ol className="audit-timeline">
          {entries.map((e) => (
            <li key={e.id} className={`audit-item action-${e.action}`}>
              <div className="audit-item-header">
                <span className="audit-action">{e.action}</span>
                <span className="audit-model">
                  {e.model_name} #{e.model_id}
                </span>
                <span className="audit-user">{e.user_name}</span>
              </div>
              <time className="audit-timestamp" dateTime={e.timestamp}>
                {formatTimestamp(e.timestamp)}
              </time>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
