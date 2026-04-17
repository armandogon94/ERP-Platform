import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type Ticket, fetchTicketsApi } from "../../api/helpdesk";
import Skeleton from "../../components/Skeleton";

const STATUSES: { value: string; label: string }[] = [
  { value: "new", label: "New" },
  { value: "assigned", label: "Assigned" },
  { value: "in_progress", label: "In Progress" },
  { value: "resolved", label: "Resolved" },
  { value: "closed", label: "Closed" },
];

export default function TicketListPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"list" | "kanban">("list");

  useEffect(() => {
    fetchTicketsApi()
      .then(setTickets)
      .catch((err: Error) => setError(err.message || "Error loading tickets"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Tickets</h1>

      <Link to="/helpdesk/tickets/new">New Ticket</Link>

      <button
        type="button"
        onClick={() => setView((v) => (v === "list" ? "kanban" : "list"))}
        style={{ marginLeft: "8px" }}
      >
        {view === "list" ? "Kanban" : "List"} view
      </button>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && view === "list" && (
        <table>
          <thead>
            <tr>
              <th>Ticket #</th>
              <th>Title</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Assignee</th>
              <th>Category</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id}>
                <td>
                  <Link to={`/helpdesk/tickets/${t.id}/edit`}>{t.ticket_number}</Link>
                </td>
                <td>{t.title}</td>
                <td>{t.priority}</td>
                <td>{t.status}</td>
                <td>{t.assignee_username ?? "—"}</td>
                <td>{t.category_name ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {!isLoading && !error && view === "kanban" && (
        <div className="kanban-board">
          {STATUSES.map((s) => {
            const columnTickets = tickets.filter((t) => t.status === s.value);
            return (
              <div key={s.value} className="kanban-column">
                <h3>
                  {s.label} ({columnTickets.length})
                </h3>
                <ul>
                  {columnTickets.map((t) => (
                    <li key={t.id} className="kanban-card">
                      <strong>{t.title}</strong>
                      <div>{t.ticket_number}</div>
                      <div>
                        {t.priority} · {t.assignee_username ?? "Unassigned"}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
