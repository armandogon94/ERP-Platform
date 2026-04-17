import { useEffect, useState } from "react";
import { type Milestone, fetchMilestonesApi } from "../../api/projects";
import Skeleton from "../../components/Skeleton";

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
    <div>
      <h1>Milestones</h1>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
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
      )}
    </div>
  );
}
