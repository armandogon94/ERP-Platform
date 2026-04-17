import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import PartnerListPage from "./PartnerListPage";

vi.mock("../../api/partners", () => ({
  fetchPartnersApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchPartnersApi } from "../../api/partners";

const mockFetchPartners = vi.mocked(fetchPartnersApi);

const samplePartners = [
  {
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
  },
  {
    id: 2,
    name: "Globex Inc",
    email: "",
    phone: "",
    is_customer: false,
    is_vendor: true,
    tax_id: "US-GLBX-1",
    payment_terms_days: 0,
    credit_limit: "0.00",
    industry_tags: [],
    address_json: {},
    notes: "",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/partners"]}>
      <Routes>
        <Route path="/partners" element={<PartnerListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("PartnerListPage", () => {
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
    mockFetchPartners.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows partner names after loading", async () => {
    mockFetchPartners.mockResolvedValueOnce(samplePartners);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Corp")).toBeInTheDocument();
      expect(screen.getByText("Globex Inc")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchPartners.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("status", { name: /loading/i })).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchPartners.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders customer / vendor flags", async () => {
    mockFetchPartners.mockResolvedValueOnce(samplePartners);
    renderPage();
    await waitFor(() => {
      // at least one "Yes" for customer flag + one "Yes" for vendor flag
      expect(screen.getAllByText(/yes/i).length).toBeGreaterThan(0);
    });
  });

  it("uses terminology for the page heading", async () => {
    mockFetchPartners.mockResolvedValueOnce(samplePartners);
    useConfigStore.setState({ terminology: { Partner: "Contact" } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/Contact/i).length).toBeGreaterThan(0);
    });
  });
});
