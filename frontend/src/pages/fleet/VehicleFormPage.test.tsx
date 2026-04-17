import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import VehicleFormPage from "./VehicleFormPage";

vi.mock("../../api/fleet", () => ({
  fetchVehicleApi: vi.fn(),
  createVehicleApi: vi.fn(),
  updateVehicleApi: vi.fn(),
  fetchDriversApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchVehicleApi,
  createVehicleApi,
  updateVehicleApi,
} from "../../api/fleet";

const mockFetch = vi.mocked(fetchVehicleApi);
const mockCreate = vi.mocked(createVehicleApi);
const mockUpdate = vi.mocked(updateVehicleApi);

const sample = {
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
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/fleet/vehicles/new"]}>
      <Routes>
        <Route path="/fleet/vehicles/new" element={<VehicleFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/fleet/vehicles/${id}/edit`]}>
      <Routes>
        <Route path="/fleet/vehicles/:id/edit" element={<VehicleFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("VehicleFormPage", () => {
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

  it("shows New Vehicle heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new vehicle/i)).toBeInTheDocument();
    });
  });

  it("pre-fills license plate when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("ABC-123")).toBeInTheDocument();
    });
  });

  it("calls createVehicleApi on submit for new vehicle", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/license plate/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/license plate/i), {
      target: { value: "NEW-1" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateVehicleApi on submit for existing vehicle", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("ABC-123")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
