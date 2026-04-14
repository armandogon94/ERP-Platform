import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import VendorListPage from "./VendorListPage";

vi.mock("../../api/purchasing", () => ({
  fetchVendorsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchVendorsApi } from "../../api/purchasing";

const mockFetchVendors = vi.mocked(fetchVendorsApi);

const sampleVendors = [
  {
    id: 1,
    name: "Acme Dental Supplies",
    email: "orders@acme.com",
    contact_name: "John Smith",
    phone: "555-0100",
    address: "",
    currency: "USD",
    payment_terms: "net_30",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    name: "MedLine Industries",
    email: "medline@example.com",
    contact_name: "",
    phone: "",
    address: "",
    currency: "USD",
    payment_terms: "net_60",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/purchasing/vendors"]}>
      <Routes>
        <Route path="/purchasing/vendors" element={<VendorListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("VendorListPage", () => {
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
    mockFetchVendors.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole("heading")).toBeInTheDocument();
  });

  it("shows vendor names after loading", async () => {
    mockFetchVendors.mockResolvedValueOnce(sampleVendors);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Acme Dental Supplies")).toBeInTheDocument();
      expect(screen.getByText("MedLine Industries")).toBeInTheDocument();
    });
  });

  it("shows loading state initially", () => {
    mockFetchVendors.mockReturnValueOnce(new Promise(() => {}));
    renderPage();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message on API failure", async () => {
    mockFetchVendors.mockRejectedValueOnce(new Error("Network Error"));
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it("renders vendor email column", async () => {
    mockFetchVendors.mockResolvedValueOnce(sampleVendors);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("orders@acme.com")).toBeInTheDocument();
    });
  });

  it("renders active status", async () => {
    mockFetchVendors.mockResolvedValueOnce(sampleVendors);
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText(/yes/i).length).toBeGreaterThan(0);
    });
  });
});
