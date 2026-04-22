import { useEffect, useState } from "react";
import ListPageShell from "../../components/ListPageShell";
import { type Milestone, fetchMilestonesApi } from "../../api/projects";

export default function MilestoneListPage() {
  const [rows, setRows] = useState<Milestone[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMilestonesApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading milestones"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title="Milestones"
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No milestones yet" }}
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Project</th>
            <th>Due</th>
            <th>Completed</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((m) => (
            <tr key={m.id}>
              <td>{m.name}</td>
              <td>{m.project_name}</td>
              <td>{m.due_date ?? "—"}</td>
              <td>{m.completed ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
