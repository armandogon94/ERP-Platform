import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import InvoiceFormPage from "./InvoiceFormPage";

vi.mock("../../api/invoicing", () => ({
  fetchInvoiceApi: vi.fn(),
  createInvoiceApi: vi.fn(),
  updateInvoiceApi: vi.fn(),
  fetchInvoicesApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchInvoiceApi,
  createInvoiceApi,
  updateInvoiceApi,
} from "../../api/invoicing";

const mockFetchInvoice = vi.mocked(fetchInvoiceApi);
const mockCreateInvoice = vi.mocked(createInvoiceApi);
const mockUpdateInvoice = vi.mocked(updateInvoiceApi);

const sampleInvoice = {
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
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/invoicing/invoices/new"]}>
      <Routes>
        <Route
          path="/invoicing/invoices/new"
          element={<InvoiceFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/invoicing/invoices/${id}/edit`]}>
      <Routes>
        <Route
          path="/invoicing/invoices/:id/edit"
          element={<InvoiceFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("InvoiceFormPage", () => {
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

  it("renders form heading for new invoice", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Invoice heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new invoice/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Invoice heading on edit route", async () => {
    mockFetchInvoice.mockResolvedValueOnce(sampleInvoice);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit invoice/i)).toBeInTheDocument();
    });
  });

  it("pre-fills invoice_number when editing", async () => {
    mockFetchInvoice.mockResolvedValueOnce(sampleInvoice);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("INV-2026-001")).toBeInTheDocument();
    });
  });

  it("pre-fills customer_name when editing", async () => {
    mockFetchInvoice.mockResolvedValueOnce(sampleInvoice);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument();
    });
  });

  it("calls createInvoiceApi on submit for new invoice", async () => {
    mockCreateInvoice.mockResolvedValueOnce(sampleInvoice);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/invoice number/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/invoice number/i), {
      target: { value: "INV-NEW-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateInvoice).toHaveBeenCalled();
    });
  });

  it("calls updateInvoiceApi on submit for existing invoice", async () => {
    mockFetchInvoice.mockResolvedValueOnce(sampleInvoice);
    mockUpdateInvoice.mockResolvedValueOnce(sampleInvoice);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("INV-2026-001")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateInvoice).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
