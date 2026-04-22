import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type Partner, fetchPartnersApi } from "../../api/partners";

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
    <ListPageShell
      title={`${partnerLabel}s`}
      actions={<Link to="/partners/new">New {partnerLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={partners.length === 0}
      empty={{ title: `No ${partnerLabel.toLowerCase()}s yet` }}
    >
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
    </ListPageShell>
  );
}
