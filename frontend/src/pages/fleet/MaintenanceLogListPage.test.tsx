import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import MaintenanceLogListPage from "./MaintenanceLogListPage";

vi.mock("../../api/fleet", () => ({
  fetchMaintenanceLogsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchMaintenanceLogsApi } from "../../api/fleet";

const mockFetch = vi.mocked(fetchMaintenanceLogsApi);

const sample = [
  {
    id: 1,
    vehicle: 7,
    vehicle_plate: "ABC-123",
    date: "2026-02-01",
    description: "Oil change",
    cost: "75.00",
    mechanic: "Joe",
    status: "scheduled",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/fleet/maintenance-logs"]}>
      <Routes>
        <Route
          path="/fleet/maintenance-logs"
          element={<MaintenanceLogListPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("MaintenanceLogListPage", () => {
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

  it("shows maintenance log entries after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("ABC-123")).toBeInTheDocument();
      expect(screen.getByText("Oil change")).toBeInTheDocument();
    });
  });
});
