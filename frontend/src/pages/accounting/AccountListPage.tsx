import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import { type Account, fetchAccountsApi } from "../../api/accounting";

export default function AccountListPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const accountLabel = useTerminology("Account", "Account");

  useEffect(() => {
    fetchAccountsApi()
      .then(setAccounts)
      .catch((err: Error) => setError(err.message || "Error loading accounts"))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div>
      <h1>Chart of {accountLabel}s</h1>

      <Link to="/accounting/accounts/new">New {accountLabel}</Link>

      {isLoading && <div>Loading...</div>}
      {error && <div role="alert">{error}</div>}

      {!isLoading && !error && (
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Type</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {accounts.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/accounting/accounts/${a.id}/edit`}>{a.code}</Link>
                </td>
                <td>{a.name}</td>
                <td>{a.account_type}</td>
                <td>{a.is_active ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
