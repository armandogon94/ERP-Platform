import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import JournalEntryFormPage from "./JournalEntryFormPage";

vi.mock("../../api/accounting", () => ({
  fetchJournalEntryApi: vi.fn(),
  createJournalEntryApi: vi.fn(),
  updateJournalEntryApi: vi.fn(),
  fetchJournalsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchJournalEntryApi,
  createJournalEntryApi,
  updateJournalEntryApi,
  fetchJournalsApi,
} from "../../api/accounting";

const mockFetchEntry = vi.mocked(fetchJournalEntryApi);
const mockCreateEntry = vi.mocked(createJournalEntryApi);
const mockUpdateEntry = vi.mocked(updateJournalEntryApi);
const mockFetchJournals = vi.mocked(fetchJournalsApi);

const sampleJournals = [
  {
    id: 1,
    name: "General Journal",
    code: "GJ",
    journal_type: "general",
    default_account: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

const sampleEntry = {
  id: 1,
  journal: 1,
  journal_name: "General Journal",
  reference: "JE-2026-001",
  entry_date: "2026-01-10",
  status: "draft",
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/accounting/entries/new"]}>
      <Routes>
        <Route path="/accounting/entries/new" element={<JournalEntryFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/accounting/entries/${id}/edit`]}>
      <Routes>
        <Route path="/accounting/entries/:id/edit" element={<JournalEntryFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("JournalEntryFormPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetchJournals.mockResolvedValue(sampleJournals);
    useConfigStore.setState({
      terminology: {},
      configs: {},
      modules: [],
      isLoading: false,
      error: null,
    });
  });

  it("renders form heading for new entry", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Journal Entry heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new journal entry/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Journal Entry heading on edit route", async () => {
    mockFetchEntry.mockResolvedValueOnce(sampleEntry);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit journal entry/i)).toBeInTheDocument();
    });
  });

  it("pre-fills reference when editing", async () => {
    mockFetchEntry.mockResolvedValueOnce(sampleEntry);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("JE-2026-001")).toBeInTheDocument();
    });
  });

  it("calls createJournalEntryApi on submit for new entry", async () => {
    mockCreateEntry.mockResolvedValueOnce(sampleEntry);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/reference/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/reference/i), {
      target: { value: "JE-NEW-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateEntry).toHaveBeenCalled();
    });
  });

  it("calls updateJournalEntryApi on submit for existing entry", async () => {
    mockFetchEntry.mockResolvedValueOnce(sampleEntry);
    mockUpdateEntry.mockResolvedValueOnce(sampleEntry);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("JE-2026-001")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateEntry).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
