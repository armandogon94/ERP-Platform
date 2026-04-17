import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type Partner, fetchPartnersApi } from "../../api/partners";
import Skeleton from "../../components/Skeleton";

export default function PartnerListPage() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const partnerLabel = useTerminology("Partner", "Partner");

  useEffect(() => {
    fetchPartnersApi()
      .then(setPartners)
      .catch((err: Error) => setError(err.message || "Error loading partners"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>{partnerLabel}s</h1>

      <Link to="/partners/new">New {partnerLabel}</Link>

      {isLoading && <Skeleton />}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Customer</th>
              <th>Vendor</th>
              <th>Tax ID</th>
            </tr>
          </thead>
          <tbody>
            {partners.map((p) => (
              <tr key={p.id}>
                <td>
                  <Link to={`/partners/${p.id}/edit`}>{p.name}</Link>
                </td>
                <td>{p.email}</td>
                <td>{p.is_customer ? "Yes" : "No"}</td>
                <td>{p.is_vendor ? "Yes" : "No"}</td>
                <td>{p.tax_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
