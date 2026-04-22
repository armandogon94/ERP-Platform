import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import TaskFormPage from "./TaskFormPage";

vi.mock("../../api/projects", () => ({
  fetchProjectsApi: vi
    .fn()
    .mockResolvedValue([
      {
        id: 1,
        name: "Apollo",
        code: "APL",
        customer: null,
        customer_name: null,
        start_date: null,
        end_date: null,
        status: "planned",
        budget: "0",
        description: "",
        created_at: "",
        updated_at: "",
      },
    ]),
  fetchTaskApi: vi.fn(),
  createTaskApi: vi.fn(),
  updateTaskApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { createTaskApi, fetchTaskApi, updateTaskApi } from "../../api/projects";

const mockCreate = vi.mocked(createTaskApi);
const mockFetch = vi.mocked(fetchTaskApi);
const mockUpdate = vi.mocked(updateTaskApi);

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/projects/tasks/new" element={<TaskFormPage />} />
        <Route path="/projects/tasks/:id/edit" element={<TaskFormPage />} />
        <Route path="/projects/tasks" element={<div>List</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("TaskFormPage", () => {
  beforeEach(() => {
    mockCreate.mockReset();
    mockFetch.mockReset();
    mockUpdate.mockReset();
  });

  it("creates a new task on submit", async () => {
    mockCreate.mockResolvedValueOnce({
      id: 7,
      project: 1,
      project_name: "Apollo",
      name: "Ship it",
      description: "",
      assignee: null,
      assignee_name: null,
      status: "todo",
      priority: "normal",
      due_date: null,
      parent_task: null,
      created_at: "",
      updated_at: "",
    });
    renderAt("/projects/tasks/new");

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /new/i })).toBeInTheDocument(),
    );
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: "Ship it" },
    });
    fireEvent.change(screen.getByLabelText(/project/i), {
      target: { value: "1" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(mockCreate).toHaveBeenCalled());
    expect(mockCreate.mock.calls[0][0]).toMatchObject({
      name: "Ship it",
      project: 1,
      status: "todo",
    });
  });

  it("loads an existing task and patches on submit", async () => {
    mockFetch.mockResolvedValueOnce({
      id: 42,
      project: 1,
      project_name: "Apollo",
      name: "Old name",
      description: "desc",
      assignee: null,
      assignee_name: null,
      status: "in_progress",
      priority: "high",
      due_date: "2026-05-01",
      parent_task: null,
      created_at: "",
      updated_at: "",
    });
    mockUpdate.mockResolvedValueOnce({} as never);
    renderAt("/projects/tasks/42/edit");

    await waitFor(() =>
      expect(screen.getByRole("heading", { name: /edit/i })).toBeInTheDocument(),
    );
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: "New name" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => expect(mockUpdate).toHaveBeenCalled());
    expect(mockUpdate.mock.calls[0][0]).toBe(42);
    expect(mockUpdate.mock.calls[0][1]).toMatchObject({ name: "New name" });
  });
});
