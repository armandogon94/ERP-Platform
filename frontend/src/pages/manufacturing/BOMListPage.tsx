import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { type BillOfMaterials, fetchBOMsApi } from "../../api/manufacturing";
import Skeleton from "../../components/Skeleton";

export default function BOMListPage() {
  const [rows, setRows] = useState<BillOfMaterials[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBOMsApi()
      .then(setRows)
      .catch((err: Error) => setError(err.message || "Error loading BOMs"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Bills of Materials</h1>

      <Link to="/manufacturing/boms/new">New BOM</Link>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Product</th>
              <th>Version</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((b) => (
              <tr key={b.id}>
                <td>
                  <Link to={`/manufacturing/boms/${b.id}/edit`}>{b.product_name}</Link>
                </td>
                <td>{b.version}</td>
                <td>{b.active ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
