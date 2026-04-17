import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import TaskListPage from "./TaskListPage";

vi.mock("../../api/projects", () => ({
  fetchTasksApi: vi.fn(),
  updateTaskApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchTasksApi } from "../../api/projects";

const mockFetch = vi.mocked(fetchTasksApi);

const sample = [
  {
    id: 1,
    project: 7,
    project_name: "North Tower",
    name: "Pour foundation",
    description: "",
    assignee: null,
    assignee_name: null,
    status: "todo",
    priority: "normal",
    due_date: null,
    parent_task: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    project: 7,
    project_name: "North Tower",
    name: "Install plumbing",
    description: "",
    assignee: null,
    assignee_name: null,
    status: "in_progress",
    priority: "high",
    due_date: null,
    parent_task: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/projects/tasks"]}>
      <Routes>
        <Route path="/projects/tasks" element={<TaskListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("TaskListPage", () => {
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

  it("renders tasks after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Pour foundation")).toBeInTheDocument();
      expect(screen.getByText("Install plumbing")).toBeInTheDocument();
    });
  });

  it("toggles between list and kanban view", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Pour foundation")).toBeInTheDocument();
    });
    const toggle = screen.getByRole("button", { name: /kanban/i });
    fireEvent.click(toggle);
    // In kanban mode, status labels appear as column headers
    await waitFor(() => {
      expect(screen.getByText(/to do/i)).toBeInTheDocument();
    });
  });
});
