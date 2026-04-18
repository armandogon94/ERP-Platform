import { useEffect, useState } from "react";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type Employee, fetchEmployeesApi } from "../../api/hr";

/** REVIEW S-4 exemplar: uses <ListPageShell /> to remove the
 * loading/error/empty repetition. Other list pages migrate on demand. */
export default function EmployeeListPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const employeeLabel = useTerminology("Employee", "Employee");

  useEffect(() => {
    fetchEmployeesApi()
      .then((data) => {
        setEmployees(data);
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading employees");
        setIsLoading(false);
      });
  }, []);

  return (
    <ListPageShell
      title={`${employeeLabel}s`}
      isLoading={isLoading}
      error={error ? `Error: ${error}` : undefined}
      isEmpty={employees.length === 0}
      empty={{ title: `No ${employeeLabel.toLowerCase()}s yet` }}
    >
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Employee #</th>
            <th>Department</th>
            <th>Job Title</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.full_name}</td>
              <td>{emp.employee_number}</td>
              <td>{emp.department_name}</td>
              <td>{emp.job_title}</td>
              <td>{emp.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
