import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type ReportTemplate, fetchReportTemplatesApi } from "../../api/reports";

export default function ReportListPage() {
  const [rows, setRows] = useState<ReportTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReportTemplatesApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading reports"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Reports</h1>

      <Link to="/reports/builder">New Report (Builder)</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Model</th>
              <th>Industry</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>{r.name}</td>
                <td>{r.model_name}</td>
                <td>{r.industry_tag}</td>
                <td>{r.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
