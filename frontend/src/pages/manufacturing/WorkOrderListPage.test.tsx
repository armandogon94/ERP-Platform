import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import WorkOrderListPage from "./WorkOrderListPage";

vi.mock("../../api/manufacturing", () => ({
  fetchWorkOrdersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchWorkOrdersApi } from "../../api/manufacturing";

const mockFetch = vi.mocked(fetchWorkOrdersApi);

const sample = [
  {
    id: 1,
    product: 5,
    product_name: "Cake",
    bom: null,
    quantity_target: "10.00",
    quantity_done: "0.00",
    status: "draft",
    start_date: null,
    end_date: null,
    notes: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/manufacturing/work-orders"]}>
      <Routes>
        <Route
          path="/manufacturing/work-orders"
          element={<WorkOrderListPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("WorkOrderListPage", () => {
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

  it("renders heading", () => {
    mockFetch.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows work orders after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Cake")).toBeInTheDocument();
      expect(screen.getByText("draft")).toBeInTheDocument();
    });
  });
});
