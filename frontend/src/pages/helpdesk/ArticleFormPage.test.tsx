import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ArticleFormPage from "./ArticleFormPage";

vi.mock("../../api/helpdesk", () => ({
  fetchArticleApi: vi.fn(),
  createArticleApi: vi.fn(),
  updateArticleApi: vi.fn(),
  fetchCategoriesApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchArticleApi,
  createArticleApi,
  updateArticleApi,
} from "../../api/helpdesk";

const mockFetch = vi.mocked(fetchArticleApi);
const mockCreate = vi.mocked(createArticleApi);
const mockUpdate = vi.mocked(updateArticleApi);

const sample = {
  id: 1,
  title: "Reset password",
  slug: "reset-password",
  body: "Body content",
  category: null,
  category_name: null,
  published: false,
  tags: [],
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/helpdesk/articles/new"]}>
      <Routes>
        <Route path="/helpdesk/articles/new" element={<ArticleFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/helpdesk/articles/${id}/edit`]}>
      <Routes>
        <Route path="/helpdesk/articles/:id/edit" element={<ArticleFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ArticleFormPage", () => {
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

  it("shows New Article heading", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new article/i)).toBeInTheDocument();
    });
  });

  it("pre-fills title when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Reset password")).toBeInTheDocument();
    });
  });

  it("calls createArticleApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: "New article" },
    });
    fireEvent.change(screen.getByLabelText(/slug/i), {
      target: { value: "new-article" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateArticleApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Reset password")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
