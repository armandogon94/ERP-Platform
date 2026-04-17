import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import VehicleListPage from "./VehicleListPage";

vi.mock("../../api/fleet", () => ({
  fetchVehiclesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchVehiclesApi } from "../../api/fleet";

const mockFetch = vi.mocked(fetchVehiclesApi);

const sample = [
  {
    id: 1,
    make: "Ford",
    model: "Transit",
    year: 2024,
    license_plate: "ABC-123",
    vin: "1FTBW2CM",
    status: "active",
    driver: null,
    driver_name: null,
    mileage: 10000,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/fleet/vehicles"]}>
      <Routes>
        <Route path="/fleet/vehicles" element={<VehicleListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("VehicleListPage", () => {
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

  it("shows vehicle plates after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("ABC-123")).toBeInTheDocument();
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

  it("uses terminology for heading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    useConfigStore.setState({ terminology: { Vehicle: "Delivery Truck" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Delivery Truck/i).length).toBeGreaterThan(0);
    });
  });
});
