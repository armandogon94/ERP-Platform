import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type Project, fetchProjectsApi } from "../../api/projects";

export default function ProjectListPage() {
  const [rows, setRows] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const projectLabel = useTerminology("Project", "Project");

  useEffect(() => {
    fetchProjectsApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading projects"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title={`${projectLabel}s`}
      actions={<Link to="/projects/projects/new">New {projectLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: `No ${projectLabel.toLowerCase()}s yet` }}
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Code</th>
            <th>Customer</th>
            <th>Status</th>
            <th>Budget</th>
            <th>Start</th>
            <th>End</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.id}>
              <td>
                <Link to={`/projects/projects/${p.id}/edit`}>{p.name}</Link>
              </td>
              <td>{p.code}</td>
              <td>{p.customer_name ?? "—"}</td>
              <td>{p.status}</td>
              <td>{p.budget}</td>
              <td>{p.start_date ?? "—"}</td>
              <td>{p.end_date ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
