import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import ArticleListPage from "./ArticleListPage";

vi.mock("../../api/helpdesk", () => ({
  fetchArticlesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchArticlesApi } from "../../api/helpdesk";

const mockFetch = vi.mocked(fetchArticlesApi);

const sample = [
  {
    id: 1,
    title: "How to reset your password",
    slug: "reset-password",
    body: "Step 1...",
    category: null,
    category_name: null,
    published: true,
    tags: [],
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/helpdesk/articles"]}>
      <Routes>
        <Route path="/helpdesk/articles" element={<ArticleListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ArticleListPage", () => {
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

  it("shows articles after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("How to reset your password")).toBeInTheDocument();
    });
  });
});
