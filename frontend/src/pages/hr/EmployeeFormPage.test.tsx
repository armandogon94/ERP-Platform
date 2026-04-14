import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import EmployeeFormPage from "./EmployeeFormPage";

vi.mock("../../api/hr", () => ({
  fetchEmployeeApi: vi.fn(),
  fetchDepartmentsApi: vi.fn(),
  createEmployeeApi: vi.fn(),
  updateEmployeeApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchEmployeeApi,
  fetchDepartmentsApi,
  createEmployeeApi,
  updateEmployeeApi,
} from "../../api/hr";

const mockFetchEmployee = vi.mocked(fetchEmployeeApi);
const mockFetchDepartments = vi.mocked(fetchDepartmentsApi);
const mockCreateEmployee = vi.mocked(createEmployeeApi);
const mockUpdateEmployee = vi.mocked(updateEmployeeApi);

const sampleDepartments = [
  { id: 1, name: "Engineering", description: "", created_at: "", updated_at: "" },
];

const sampleEmployee = {
  id: 1,
  employee_number: "EMP-001",
  first_name: "Alice",
  last_name: "Smith",
  full_name: "Alice Smith",
  email: "alice@example.com",
  department: 1,
  department_name: "Engineering",
  job_title: "Engineer",
  hire_date: "2024-01-15",
  status: "active",
  employee_type: "full_time",
  created_at: "2024-01-15T00:00:00Z",
  updated_at: "2024-01-15T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/hr/employees/new"]}>
      <Routes>
        <Route path="/hr/employees/new" element={<EmployeeFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/hr/employees/${id}/edit`]}>
      <Routes>
        <Route path="/hr/employees/:id/edit" element={<EmployeeFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("EmployeeFormPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useConfigStore.setState({
      terminology: {},
      configs: {},
      modules: [],
      isLoading: false,
      error: null,
    });
    mockFetchDepartments.mockResolvedValue(sampleDepartments);
  });

  it("renders form heading for new employee", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Employee heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new employee/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Employee heading on edit route", async () => {
    mockFetchEmployee.mockResolvedValueOnce(sampleEmployee);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit employee/i)).toBeInTheDocument();
    });
  });

  it("pre-fills form fields when editing", async () => {
    mockFetchEmployee.mockResolvedValueOnce(sampleEmployee);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Alice")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Smith")).toBeInTheDocument();
      expect(screen.getByDisplayValue("alice@example.com")).toBeInTheDocument();
    });
  });

  it("calls createEmployeeApi on submit for new employee", async () => {
    mockCreateEmployee.mockResolvedValueOnce(sampleEmployee);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/first name/i), {
      target: { value: "Bob" },
    });
    fireEvent.change(screen.getByLabelText(/last name/i), {
      target: { value: "Jones" },
    });
    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "bob@example.com" },
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateEmployee).toHaveBeenCalled();
    });
  });

  it("calls updateEmployeeApi on submit for existing employee", async () => {
    mockFetchEmployee.mockResolvedValueOnce(sampleEmployee);
    mockUpdateEmployee.mockResolvedValueOnce(sampleEmployee);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("Alice")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateEmployee).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("uses terminology for form label", async () => {
    useConfigStore.setState({ terminology: { Employee: "Staff Member" } });
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/staff member/i)).toBeInTheDocument();
    });
  });
});
