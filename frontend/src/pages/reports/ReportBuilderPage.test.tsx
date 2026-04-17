import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ReportBuilderPage from "./ReportBuilderPage";

vi.mock("../../api/reports", () => ({
  fetchAggregateApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

beforeEach(() => {
  // @ts-expect-error jsdom polyfill
  global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

import { fetchAggregateApi } from "../../api/reports";

const mockFetch = vi.mocked(fetchAggregateApi);

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/reports/builder"]}>
      <Routes>
        <Route path="/reports/builder" element={<ReportBuilderPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ReportBuilderPage", () => {
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
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("fetches aggregate when Run Report clicked", async () => {
    mockFetch.mockResolvedValueOnce([
      { group: "draft", value: 150 },
      { group: "paid", value: 200 },
    ]);
    renderPage();
    fireEvent.click(screen.getByRole("button", { name: /run report/i }));
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    });
  });

  it("renders pivot results after fetching", async () => {
    mockFetch.mockResolvedValueOnce([
      { group: "draft", value: 150 },
      { group: "paid", value: 200 },
    ]);
    renderPage();
    fireEvent.click(screen.getByRole("button", { name: /run report/i }));
    await waitFor(() => {
      expect(screen.getByText("draft")).toBeInTheDocument();
      expect(screen.getByText("paid")).toBeInTheDocument();
    });
  });
});
