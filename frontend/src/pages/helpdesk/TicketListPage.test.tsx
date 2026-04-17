import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import TicketListPage from "./TicketListPage";

vi.mock("../../api/helpdesk", () => ({
  fetchTicketsApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchTicketsApi } from "../../api/helpdesk";

const mockFetch = vi.mocked(fetchTicketsApi);

const sample = [
  {
    id: 1,
    ticket_number: "TKT/2026/00001",
    title: "Login broken",
    description: "",
    category: null,
    category_name: null,
    reporter_partner: null,
    reporter_partner_name: null,
    reporter_user: null,
    assignee: null,
    assignee_username: null,
    priority: "high",
    status: "new",
    resolved_at: null,
    sla_breached: false,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    ticket_number: "TKT/2026/00002",
    title: "Refund request",
    description: "",
    category: null,
    category_name: null,
    reporter_partner: null,
    reporter_partner_name: null,
    reporter_user: null,
    assignee: null,
    assignee_username: null,
    priority: "normal",
    status: "in_progress",
    resolved_at: null,
    sla_breached: false,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
];

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/helpdesk/tickets"]}>
      <Routes>
        <Route path="/helpdesk/tickets" element={<TicketListPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("TicketListPage", () => {
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

  it("renders tickets after loading", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Login broken")).toBeInTheDocument();
      expect(screen.getByText("Refund request")).toBeInTheDocument();
    });
  });

  it("toggles between list and kanban view", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Login broken")).toBeInTheDocument();
    });
    const toggle = screen.getByRole("button", { name: /kanban/i });
    fireEvent.click(toggle);
    await waitFor(() => {
      // Kanban column "In Progress" header appears only in kanban mode
      expect(screen.getByText(/in progress/i)).toBeInTheDocument();
    });
  });
});
