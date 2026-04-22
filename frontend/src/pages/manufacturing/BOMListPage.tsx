import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { type BillOfMaterials, fetchBOMsApi } from "../../api/manufacturing";

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
    <ListPageShell
      title="Bills of Materials"
      actions={<Link to="/manufacturing/boms/new">New BOM</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={rows.length === 0}
      empty={{ title: "No bills of materials yet" }}
    >
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
    </ListPageShell>
  );
}
