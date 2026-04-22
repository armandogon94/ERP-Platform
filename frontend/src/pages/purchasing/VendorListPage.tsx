import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type Vendor, fetchVendorsApi } from "../../api/purchasing";

export default function VendorListPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const vendorLabel = useTerminology("Vendor", "Vendor");

  useEffect(() => {
    fetchVendorsApi()
      .then(setVendors)
      .catch((err: Error) => setError(err.message || "Error loading vendors"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <ListPageShell
      title={`${vendorLabel}s`}
      actions={<Link to="/purchasing/vendors/new">New {vendorLabel}</Link>}
      isLoading={isLoading}
      error={error || undefined}
      isEmpty={vendors.length === 0}
      empty={{ title: `No ${vendorLabel.toLowerCase()}s yet` }}
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Payment Terms</th>
            <th>Active</th>
          </tr>
        </thead>
        <tbody>
          {vendors.map((v) => (
            <tr key={v.id}>
              <td>
                <Link to={`/purchasing/vendors/${v.id}/edit`}>{v.name}</Link>
              </td>
              <td>{v.email}</td>
              <td>{v.payment_terms}</td>
              <td>{v.is_active ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
