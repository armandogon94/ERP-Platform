import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import InvoiceListPage from "./InvoiceListPage";

vi.mock("../../api/invoicing", () => ({
  fetchInvoicesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchInvoicesApi } from "../../api/invoicing";

const mockFetchInvoices = vi.mocked(fetchInvoicesApi);

const sampleInvoices = [
  {
    id: 1,
    invoice_number: "INV-2026-001",
    invoice_type: "customer",
    status: "draft",
    customer_name: "Acme Corp",
    customer_email: "acme@example.com",
    invoice_date: "2026-01-10",
    due_date: "2026-02-10",
    notes: "",
    subtotal: "450.00",
    tax_amount: "50.00",
    total_amount: "500.00",
    amount_paid: "0.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    invoice_number: "INV-2026-002",
    invoice_type: "customer",
    status: "posted",
    customer_name: "Globex Inc",
    customer_email: "",
    invoice_date: "2026-01-15",
    due_date: "2026-02-15",
    notes: "",
    subtotal: "900.00",
    tax_amount: "100.00",
    total_amount: "1000.00",
    amount_paid: "1000.00",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/invoicing/invoices"]}>
      <Routes>
        <Route path="/invoicing/invoices" element={<InvoiceListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("InvoiceListPage", () => {
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
    mockFetchInvoices.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows invoice numbers after loading", async () => {
    mockFetchInvoices.mockResolvedValueOnce(sampleInvoices);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("INV-2026-001")).toBeInTheDocument();
      expect(screen.getByText("INV-2026-002")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchInvoices.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchInvoices.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders customer name column", async () => {
    mockFetchInvoices.mockResolvedValueOnce(sampleInvoices);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Corp")).toBeInTheDocument();
    });
  });

  it("renders status column", async () => {
    mockFetchInvoices.mockResolvedValueOnce(sampleInvoices);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("draft")).toBeInTheDocument();
    });
  });

  it("renders total amount column", async () => {
    mockFetchInvoices.mockResolvedValueOnce(sampleInvoices);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("500.00")).toBeInTheDocument();
    });
  });

  it("uses terminology for the page heading", async () => {
    mockFetchInvoices.mockResolvedValueOnce(sampleInvoices);
    useConfigStore.setState({ terminology: { Invoice: "Guest Check" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Guest Check/i).length).toBeGreaterThan(0);
    });
  });
});
