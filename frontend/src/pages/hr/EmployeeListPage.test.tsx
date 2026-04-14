import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import EmployeeListPage from "./EmployeeListPage";

vi.mock("../../api/hr", () => ({
  fetchEmployeesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchEmployeesApi } from "../../api/hr";

const mockFetchEmployees = vi.mocked(fetchEmployeesApi);

const sampleEmployees = [
  {
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
  },
  {
    id: 2,
    employee_number: "EMP-002",
    first_name: "Bob",
    last_name: "Jones",
    full_name: "Bob Jones",
    email: "bob@example.com",
    department: 1,
    department_name: "Engineering",
    job_title: "Senior Engineer",
    hire_date: "2023-06-01",
    status: "active",
    employee_type: "full_time",
    created_at: "2023-06-01T00:00:00Z",
    updated_at: "2023-06-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/hr/employees"]}>
      <Routes>
        <Route path="/hr/employees" element={<EmployeeListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("EmployeeListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useConfigStore.setState({
      terminology: {},
      configs: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("renders page heading", async () => {
    mockFetchEmployees.mockResolvedValueOnce(sampleEmployees);
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows employee names after loading", async () => {
    mockFetchEmployees.mockResolvedValueOnce(sampleEmployees);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Alice Smith")).toBeInTheDocument();
      expect(screen.getByText("Bob Jones")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchEmployees.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchEmployees.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("uses terminology for the page label", async () => {
    mockFetchEmployees.mockResolvedValueOnce(sampleEmployees);
    useConfigStore.setState({ terminology: { Employee: "Staff Member" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/Staff Member/i)).toBeInTheDocument();
    });
  });

  it("renders department column", async () => {
    mockFetchEmployees.mockResolvedValueOnce(sampleEmployees);
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText("Engineering").length).toBeGreaterThan(0);
    });
  });
});
