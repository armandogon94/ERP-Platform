import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type Department,
  type Employee,
  createEmployeeApi,
  fetchDepartmentsApi,
  fetchEmployeeApi,
  updateEmployeeApi,
} from "../../api/hr";

interface FormState {
  first_name: string;
  last_name: string;
  email: string;
  job_title: string;
  hire_date: string;
  department: string;
  status: string;
  employee_type: string;
}

const EMPTY_FORM: FormState = {
  first_name: "",
  last_name: "",
  email: "",
  job_title: "",
  hire_date: "",
  department: "",
  status: "active",
  employee_type: "full_time",
};

export default function EmployeeFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const employeeLabel = useTerminology("Employee", "Employee");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    fetchDepartmentsApi().catch(() => {
      // non-blocking
    });

    fetchDepartmentsApi()
      .then(setDepartments)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchEmployeeApi(Number(id))
      .then((emp: Employee) => {
        setForm({
          first_name: emp.first_name,
          last_name: emp.last_name,
          email: emp.email,
          job_title: emp.job_title,
          hire_date: emp.hire_date,
          department: emp.department ? String(emp.department) : "",
          status: emp.status,
          employee_type: emp.employee_type,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading employee");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const payload = {
      ...form,
      department: form.department ? Number(form.department) : null,
    };
    try {
      if (isEdit && id) {
        await updateEmployeeApi(Number(id), payload);
      } else {
        await createEmployeeApi(payload);
      }
      navigate("/hr/employees");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>
        {headingPrefix} {employeeLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="first_name">First Name</label>
          <input
            id="first_name"
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="last_name">Last Name</label>
          <input
            id="last_name"
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="job_title">Job Title</label>
          <input
            id="job_title"
            name="job_title"
            value={form.job_title}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="hire_date">Hire Date</label>
          <input
            id="hire_date"
            name="hire_date"
            type="date"
            value={form.hire_date}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="department">Department</label>
          <select
            id="department"
            name="department"
            value={form.department}
            onChange={handleChange}
          >
            <option value="">— Select —</option>
            {departments.map((dept) => (
              <option key={dept.id} value={dept.id}>
                {dept.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select id="status" name="status" value={form.status} onChange={handleChange}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="terminated">Terminated</option>
            <option value="on_leave">On Leave</option>
          </select>
        </div>

        <div>
          <label htmlFor="employee_type">Employee Type</label>
          <select
            id="employee_type"
            name="employee_type"
            value={form.employee_type}
            onChange={handleChange}
          >
            <option value="full_time">Full Time</option>
            <option value="part_time">Part Time</option>
            <option value="contractor">Contractor</option>
            <option value="intern">Intern</option>
          </select>
        </div>

        <button type="submit">Save</button>
      </form>
    </div>
  );
}
