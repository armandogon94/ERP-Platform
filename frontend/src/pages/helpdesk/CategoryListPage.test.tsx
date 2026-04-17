import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import CategoryListPage from "./CategoryListPage";

vi.mock("../../api/helpdesk", () => ({
  fetchCategoriesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchCategoriesApi } from "../../api/helpdesk";

const mockFetch = vi.mocked(fetchCategoriesApi);

const sample = [
  {
    id: 1,
    name: "Billing",
    sla_hours: 24,
    industry_tag: "",
    description: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/helpdesk/categories"]}>
      <Routes>
        <Route path="/helpdesk/categories" element={<CategoryListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("CategoryListPage", () => {
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

  it("shows categories after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Billing")).toBeInTheDocument();
    });
  });
});
