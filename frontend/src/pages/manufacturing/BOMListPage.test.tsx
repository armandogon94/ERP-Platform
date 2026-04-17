import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import BOMListPage from "./BOMListPage";

vi.mock("../../api/manufacturing", () => ({
  fetchBOMsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchBOMsApi } from "../../api/manufacturing";

const mockFetch = vi.mocked(fetchBOMsApi);

const sample = [
  {
    id: 1,
    product: 5,
    product_name: "Cake",
    version: "1.0",
    active: true,
    notes: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/manufacturing/boms"]}>
      <Routes>
        <Route path="/manufacturing/boms" element={<BOMListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("BOMListPage", () => {
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

  it("shows BOMs after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Cake")).toBeInTheDocument();
      expect(screen.getByText("1.0")).toBeInTheDocument();
    });
  });
});
