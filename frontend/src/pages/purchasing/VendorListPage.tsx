import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
    <div>
      <h1>{vendorLabel}s</h1>

      <Link to="/purchasing/vendors/new">New {vendorLabel}</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
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
      )}
    </div>
  );
}
