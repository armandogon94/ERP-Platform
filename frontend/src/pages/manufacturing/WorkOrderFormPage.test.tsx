import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import WorkOrderFormPage from "./WorkOrderFormPage";

vi.mock("../../api/manufacturing", () => ({
  fetchWorkOrderApi: vi.fn(),
  createWorkOrderApi: vi.fn(),
  updateWorkOrderApi: vi.fn(),
  startWorkOrderApi: vi.fn(),
  completeWorkOrderApi: vi.fn(),
  fetchBOMsApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/inventory", () => ({
  fetchProductsApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchWorkOrderApi,
  createWorkOrderApi,
  updateWorkOrderApi,
  startWorkOrderApi,
  completeWorkOrderApi,
} from "../../api/manufacturing";

const mockFetch = vi.mocked(fetchWorkOrderApi);
const mockCreate = vi.mocked(createWorkOrderApi);
const mockUpdate = vi.mocked(updateWorkOrderApi);
const mockStart = vi.mocked(startWorkOrderApi);
const mockComplete = vi.mocked(completeWorkOrderApi);

const sample = {
  id: 1,
  product: 5,
  product_name: "Cake",
  bom: null,
  quantity_target: "10.00",
  quantity_done: "0.00",
  status: "in_progress",
  start_date: "2026-04-17",
  end_date: null,
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/manufacturing/work-orders/${id}/edit`]}>
      <Routes>
        <Route
          path="/manufacturing/work-orders/:id/edit"
          element={<WorkOrderFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("WorkOrderFormPage", () => {
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

  it("pre-fills quantity_target when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("10.00")).toBeInTheDocument();
    });
  });

  it("shows Start button when status is confirmed or draft", async () => {
    mockFetch.mockResolvedValueOnce({ ...sample, status: "confirmed" });
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /start/i })).toBeInTheDocument();
    });
  });

  it("shows Complete button when status is in_progress", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /complete/i })).toBeInTheDocument();
    });
  });

  it("calls completeWorkOrderApi on Complete click", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockComplete.mockResolvedValueOnce({ ...sample, status: "done" });
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /complete/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /complete/i }));
    await waitFor(() => {
      expect(mockComplete).toHaveBeenCalledWith(1);
    });
  });
});
