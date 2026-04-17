import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import MilestoneListPage from "./MilestoneListPage";

vi.mock("../../api/projects", () => ({
  fetchMilestonesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchMilestonesApi } from "../../api/projects";

const mockFetch = vi.mocked(fetchMilestonesApi);

const sample = [
  {
    id: 1,
    project: 7,
    project_name: "North Tower",
    name: "Phase 1 complete",
    due_date: "2026-06-30",
    completed: false,
    completed_at: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/projects/milestones"]}>
      <Routes>
        <Route path="/projects/milestones" element={<MilestoneListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("MilestoneListPage", () => {
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

  it("shows milestone rows after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Phase 1 complete")).toBeInTheDocument();
      expect(screen.getByText("North Tower")).toBeInTheDocument();
    });
  });
});
