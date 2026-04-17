import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ProjectFormPage from "./ProjectFormPage";

vi.mock("../../api/projects", () => ({
  fetchProjectApi: vi.fn(),
  createProjectApi: vi.fn(),
  updateProjectApi: vi.fn(),
}));

vi.mock("../../api/partners", () => ({
  fetchPartnersApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchProjectApi,
  createProjectApi,
  updateProjectApi,
} from "../../api/projects";

const mockFetch = vi.mocked(fetchProjectApi);
const mockCreate = vi.mocked(createProjectApi);
const mockUpdate = vi.mocked(updateProjectApi);

const sample = {
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
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/projects/projects/new"]}>
      <Routes>
        <Route path="/projects/projects/new" element={<ProjectFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/projects/projects/${id}/edit`]}>
      <Routes>
        <Route
          path="/projects/projects/:id/edit"
          element={<ProjectFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProjectFormPage", () => {
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

  it("shows New Project heading", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new project/i)).toBeInTheDocument();
    });
  });

  it("pre-fills name when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("North Tower")).toBeInTheDocument();
    });
  });

  it("calls createProjectApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/^name/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/^name/i), {
      target: { value: "New Project" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateProjectApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("North Tower")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
