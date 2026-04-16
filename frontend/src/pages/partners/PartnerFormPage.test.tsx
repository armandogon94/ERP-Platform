import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import PartnerFormPage from "./PartnerFormPage";

vi.mock("../../api/partners", () => ({
  fetchPartnerApi: vi.fn(),
  createPartnerApi: vi.fn(),
  updatePartnerApi: vi.fn(),
  fetchPartnersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchPartnerApi,
  createPartnerApi,
  updatePartnerApi,
} from "../../api/partners";

const mockFetchPartner = vi.mocked(fetchPartnerApi);
const mockCreatePartner = vi.mocked(createPartnerApi);
const mockUpdatePartner = vi.mocked(updatePartnerApi);

const samplePartner = {
  id: 1,
  name: "Acme Corp",
  email: "orders@acme.com",
  phone: "555-0100",
  is_customer: true,
  is_vendor: false,
  tax_id: "US-ACME-1",
  payment_terms_days: 30,
  credit_limit: "50000.00",
  industry_tags: [],
  address_json: {},
  notes: "",
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/partners/new"]}>
      <Routes>
        <Route path="/partners/new" element={<PartnerFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/partners/${id}/edit`]}>
      <Routes>
        <Route path="/partners/:id/edit" element={<PartnerFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PartnerFormPage", () => {
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

  it("shows New Partner heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new partner/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Partner heading on edit route", async () => {
    mockFetchPartner.mockResolvedValueOnce(samplePartner);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit partner/i)).toBeInTheDocument();
    });
  });

  it("pre-fills name when editing", async () => {
    mockFetchPartner.mockResolvedValueOnce(samplePartner);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument();
    });
  });

  it("calls createPartnerApi on submit for new partner", async () => {
    mockCreatePartner.mockResolvedValueOnce(samplePartner);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/^name/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/^name/i), {
      target: { value: "New Partner" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreatePartner).toHaveBeenCalled();
    });
  });

  it("calls updatePartnerApi on submit for existing partner", async () => {
    mockFetchPartner.mockResolvedValueOnce(samplePartner);
    mockUpdatePartner.mockResolvedValueOnce(samplePartner);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("Acme Corp")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdatePartner).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });
});
