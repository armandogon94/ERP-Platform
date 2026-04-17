import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ProjectListPage from "./ProjectListPage";

vi.mock("../../api/projects", () => ({
  fetchProjectsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchProjectsApi } from "../../api/projects";

const mockFetch = vi.mocked(fetchProjectsApi);

const sample = [
  {
    id: 1,
    name: "North Tower",
    code: "NT-1",
    customer: null,
    customer_name: null,
    start_date: "2026-01-01",
    end_date: null,
    status: "active",
    budget: "1000000.00",
    description: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/projects/projects"]}>
      <Routes>
        <Route path="/projects/projects" element={<ProjectListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProjectListPage", () => {
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

  it("shows project name after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("North Tower")).toBeInTheDocument();
    });
  });

  it("shows loading state", () => {
    mockFetch.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error state", async () => {
    mockFetch.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("uses terminology for heading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    useConfigStore.setState({ terminology: { Project: "Job Site" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Job Site/i).length).toBeGreaterThan(0);
    });
  });
});
