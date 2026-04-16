import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import QuotationFormPage from "./QuotationFormPage";

vi.mock("../../api/sales", () => ({
  fetchQuotationApi: vi.fn(),
  createQuotationApi: vi.fn(),
  updateQuotationApi: vi.fn(),
  fetchQuotationsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchQuotationApi,
  createQuotationApi,
  updateQuotationApi,
} from "../../api/sales";

const mockFetchQuotation = vi.mocked(fetchQuotationApi);
const mockCreateQuotation = vi.mocked(createQuotationApi);
const mockUpdateQuotation = vi.mocked(updateQuotationApi);

const sampleQuotation = {
  id: 1,
  quotation_number: "QUO-2026-001",
  customer_name: "Acme Corp",
  customer_email: "acme@example.com",
  status: "draft",
  valid_until: "2026-03-01",
  notes: "",
  total_amount: "250.00",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/sales/quotations/new"]}>
      <Routes>
        <Route path="/sales/quotations/new" element={<QuotationFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/sales/quotations/${id}/edit`]}>
      <Routes>
        <Route path="/sales/quotations/:id/edit" element={<QuotationFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("QuotationFormPage", () => {
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

  it("renders form heading for new quotation", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Quotation heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new quotation/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Quotation heading on edit route", async () => {
    mockFetchQuotation.mockResolvedValueOnce(sampleQuotation);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit quotation/i)).toBeInTheDocument();
    });
  });

  it("pre-fills quotation_number when editing", async () => {
    mockFetchQuotation.mockResolvedValueOnce(sampleQuotation);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("QUO-2026-001")).toBeInTheDocument();
    });
  });

  it("pre-fills customer_name when editing", async () => {
    mockFetchQuotation.mockResolvedValueOnce(sampleQuotation);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument();
    });
  });

  it("calls createQuotationApi on submit for new quotation", async () => {
    mockCreateQuotation.mockResolvedValueOnce(sampleQuotation);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/quotation number/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/quotation number/i), {
      target: { value: "QUO-NEW-001" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateQuotation).toHaveBeenCalled();
    });
  });

  it("calls updateQuotationApi on submit for existing quotation", async () => {
    mockFetchQuotation.mockResolvedValueOnce(sampleQuotation);
    mockUpdateQuotation.mockResolvedValueOnce(sampleQuotation);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("QUO-2026-001")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateQuotation).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("uses terminology for the form heading", async () => {
    useConfigStore.setState({ terminology: { Quotation: "Proposal" } });
    renderNewForm();
    await waitFor(() => {
      expect(screen.getAllByText(/Proposal/i).length).toBeGreaterThan(0);
    });
  });
});
