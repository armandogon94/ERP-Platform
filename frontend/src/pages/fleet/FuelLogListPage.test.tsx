import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import FuelLogListPage from "./FuelLogListPage";

vi.mock("../../api/fleet", () => ({
  fetchFuelLogsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchFuelLogsApi } from "../../api/fleet";

const mockFetch = vi.mocked(fetchFuelLogsApi);

const sample = [
  {
    id: 1,
    vehicle: 7,
    vehicle_plate: "ABC-123",
    date: "2026-03-01",
    liters: "42.50",
    cost_per_liter: "1.400",
    total_cost: "59.50",
    mileage_at_fill: 12000,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/fleet/fuel-logs"]}>
      <Routes>
        <Route path="/fleet/fuel-logs" element={<FuelLogListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("FuelLogListPage", () => {
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

  it("shows fuel entries after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("ABC-123")).toBeInTheDocument();
      expect(screen.getByText("59.50")).toBeInTheDocument();
    });
  });
});
