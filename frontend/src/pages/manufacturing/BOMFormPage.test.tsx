import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import BOMFormPage from "./BOMFormPage";

vi.mock("../../api/manufacturing", () => ({
  fetchBOMApi: vi.fn(),
  createBOMApi: vi.fn(),
  updateBOMApi: vi.fn(),
  fetchBOMLinesApi: vi.fn().mockResolvedValue([]),
  createBOMLineApi: vi.fn(),
  deleteBOMLineApi: vi.fn(),
}));

vi.mock("../../api/inventory", () => ({
  fetchProductsApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchBOMApi,
  createBOMApi,
  updateBOMApi,
} from "../../api/manufacturing";

const mockFetch = vi.mocked(fetchBOMApi);
const mockCreate = vi.mocked(createBOMApi);
const mockUpdate = vi.mocked(updateBOMApi);

const sample = {
  id: 1,
  product: 5,
  product_name: "Cake",
  version: "1.0",
  active: true,
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/manufacturing/boms/new"]}>
      <Routes>
        <Route path="/manufacturing/boms/new" element={<BOMFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/manufacturing/boms/${id}/edit`]}>
      <Routes>
        <Route path="/manufacturing/boms/:id/edit" element={<BOMFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("BOMFormPage", () => {
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

  it("shows New BOM heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new bom/i)).toBeInTheDocument();
    });
  });

  it("pre-fills version when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("1.0")).toBeInTheDocument();
    });
  });

  it("calls createBOMApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/version/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/version/i), {
      target: { value: "2.0" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateBOMApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("1.0")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
