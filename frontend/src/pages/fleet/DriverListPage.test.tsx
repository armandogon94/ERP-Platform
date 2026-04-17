import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import DriverListPage from "./DriverListPage";

vi.mock("../../api/fleet", () => ({
  fetchDriversApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchDriversApi } from "../../api/fleet";

const mockFetch = vi.mocked(fetchDriversApi);

const sample = [
  {
    id: 1,
    name: "Alice Driver",
    license_number: "DL-001",
    license_expiry: "2030-01-01",
    phone: "555-0100",
    status: "active",
    employee: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/fleet/drivers"]}>
      <Routes>
        <Route path="/fleet/drivers" element={<DriverListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("DriverListPage", () => {
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

  it("renders page heading", () => {
    mockFetch.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows driver names after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Alice Driver")).toBeInTheDocument();
    });
  });

  it("shows loading state", () => {
    mockFetch.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("shows error on API failure", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
