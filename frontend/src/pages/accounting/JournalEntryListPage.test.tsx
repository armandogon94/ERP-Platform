import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import JournalEntryListPage from "./JournalEntryListPage";

vi.mock("../../api/accounting", () => ({
  fetchJournalEntriesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchJournalEntriesApi } from "../../api/accounting";

const mockFetchEntries = vi.mocked(fetchJournalEntriesApi);

const sampleEntries = [
  {
    id: 1,
    journal: 1,
    journal_name: "General Journal",
    reference: "JE-2026-001",
    entry_date: "2026-01-10",
    status: "draft",
    notes: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    journal: 1,
    journal_name: "General Journal",
    reference: "JE-2026-002",
    entry_date: "2026-01-15",
    status: "posted",
    notes: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/accounting/entries"]}>
      <Routes>
        <Route path="/accounting/entries" element={<JournalEntryListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("JournalEntryListPage", () => {
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

  it("renders page heading", () => {
    mockFetchEntries.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows entry references after loading", async () => {
    mockFetchEntries.mockResolvedValueOnce(sampleEntries);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("JE-2026-001")).toBeInTheDocument();
      expect(screen.getByText("JE-2026-002")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchEntries.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchEntries.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders journal name column", async () => {
    mockFetchEntries.mockResolvedValueOnce(sampleEntries);
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText("General Journal").length).toBeGreaterThan(0);
    });
  });

  it("renders status column", async () => {
    mockFetchEntries.mockResolvedValueOnce(sampleEntries);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("draft")).toBeInTheDocument();
    });
  });
});
