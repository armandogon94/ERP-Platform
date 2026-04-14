import { useEffect, useState } from "react";
import { useTerminology } from "../../hooks/useTerminology";
import { type Employee, fetchEmployeesApi } from "../../api/hr";

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
    <div>
      <h1>{employeeLabel}s</h1>

      {isLoading && <div>Loading...</div>}

      {error && <div>Error: {error}</div>}

      {!isLoading && !error && (
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
      )}
    </div>
  );
}
