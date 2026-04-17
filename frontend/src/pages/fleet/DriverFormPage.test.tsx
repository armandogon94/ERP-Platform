import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import DriverFormPage from "./DriverFormPage";

vi.mock("../../api/fleet", () => ({
  fetchDriverApi: vi.fn(),
  createDriverApi: vi.fn(),
  updateDriverApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchDriverApi,
  createDriverApi,
  updateDriverApi,
} from "../../api/fleet";

const mockFetch = vi.mocked(fetchDriverApi);
const mockCreate = vi.mocked(createDriverApi);
const mockUpdate = vi.mocked(updateDriverApi);

const sample = {
  id: 1,
  name: "Alice Driver",
  license_number: "DL-001",
  license_expiry: "2030-01-01",
  phone: "555-0100",
  status: "active",
  employee: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/fleet/drivers/new"]}>
      <Routes>
        <Route path="/fleet/drivers/new" element={<DriverFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/fleet/drivers/${id}/edit`]}>
      <Routes>
        <Route path="/fleet/drivers/:id/edit" element={<DriverFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("DriverFormPage", () => {
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

  it("shows New Driver heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new driver/i)).toBeInTheDocument();
    });
  });

  it("pre-fills name when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Alice Driver")).toBeInTheDocument();
    });
  });

  it("calls createDriverApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/^name/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/^name/i), {
      target: { value: "New Driver" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateDriverApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Alice Driver")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
