import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import AccountListPage from "./AccountListPage";

vi.mock("../../api/accounting", () => ({
  fetchAccountsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchAccountsApi } from "../../api/accounting";

const mockFetchAccounts = vi.mocked(fetchAccountsApi);

const sampleAccounts = [
  {
    id: 1,
    code: "1000",
    name: "Cash",
    account_type: "asset",
    parent: null,
    parent_name: null,
    description: "",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    code: "4000",
    name: "Revenue",
    account_type: "revenue",
    parent: null,
    parent_name: null,
    description: "",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/accounting/accounts"]}>
      <Routes>
        <Route path="/accounting/accounts" element={<AccountListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("AccountListPage", () => {
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
    mockFetchAccounts.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows account names after loading", async () => {
    mockFetchAccounts.mockResolvedValueOnce(sampleAccounts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Cash")).toBeInTheDocument();
      expect(screen.getByText("Revenue")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchAccounts.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchAccounts.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders account code column", async () => {
    mockFetchAccounts.mockResolvedValueOnce(sampleAccounts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("1000")).toBeInTheDocument();
    });
  });

  it("renders account type column", async () => {
    mockFetchAccounts.mockResolvedValueOnce(sampleAccounts);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("asset")).toBeInTheDocument();
    });
  });
});
