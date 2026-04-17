import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import POSSessionListPage from "./POSSessionListPage";

vi.mock("../../api/pos", () => ({
  fetchPOSSessionsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchPOSSessionsApi } from "../../api/pos";

const mockFetch = vi.mocked(fetchPOSSessionsApi);

const sample = [
  {
    id: 1,
    station: "Bar-1",
    cash_on_open: "100.00",
    cash_on_close: null,
    expected_cash: null,
    variance: null,
    opened_by: 1,
    opened_by_username: "admin",
    opened_at: "2026-04-17T10:00:00Z",
    closed_at: null,
    status: "open",
    notes: "",
    created_at: "2026-04-17T10:00:00Z",
    updated_at: "2026-04-17T10:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/pos/sessions"]}>
      <Routes>
        <Route path="/pos/sessions" element={<POSSessionListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("POSSessionListPage", () => {
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

  it("shows sessions after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Bar-1")).toBeInTheDocument();
      expect(screen.getByText("open")).toBeInTheDocument();
    });
  });
});
