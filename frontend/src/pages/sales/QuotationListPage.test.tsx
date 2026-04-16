import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import QuotationListPage from "./QuotationListPage";

vi.mock("../../api/sales", () => ({
  fetchQuotationsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchQuotationsApi } from "../../api/sales";

const mockFetchQuotations = vi.mocked(fetchQuotationsApi);

const sampleQuotations = [
  {
    id: 1,
    quotation_number: "QUO-2026-001",
    customer_name: "Acme Corp",
    customer_email: "acme@example.com",
    status: "draft",
    valid_until: null,
    notes: "",
    total_amount: "300.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    quotation_number: "QUO-2026-002",
    customer_name: "Globex Inc",
    customer_email: "",
    status: "sent",
    valid_until: "2026-02-01",
    notes: "",
    total_amount: "750.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/sales/quotations"]}>
      <Routes>
        <Route path="/sales/quotations" element={<QuotationListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("QuotationListPage", () => {
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
    mockFetchQuotations.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows quotation numbers after loading", async () => {
    mockFetchQuotations.mockResolvedValueOnce(sampleQuotations);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("QUO-2026-001")).toBeInTheDocument();
      expect(screen.getByText("QUO-2026-002")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchQuotations.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchQuotations.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders customer name column", async () => {
    mockFetchQuotations.mockResolvedValueOnce(sampleQuotations);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    });
  });

  it("renders status column", async () => {
    mockFetchQuotations.mockResolvedValueOnce(sampleQuotations);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("draft")).toBeInTheDocument();
    });
  });

  it("uses terminology for the page heading", async () => {
    mockFetchQuotations.mockResolvedValueOnce(sampleQuotations);
    useConfigStore.setState({ terminology: { Quotation: "Proposal" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Proposal/i).length).toBeGreaterThan(0);
    });
  });
});
