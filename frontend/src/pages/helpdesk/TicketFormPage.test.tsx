import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import TicketFormPage from "./TicketFormPage";

vi.mock("../../api/helpdesk", () => ({
  fetchTicketApi: vi.fn(),
  createTicketApi: vi.fn(),
  updateTicketApi: vi.fn(),
  resolveTicketApi: vi.fn(),
  reopenTicketApi: vi.fn(),
  fetchCategoriesApi: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import {
  fetchTicketApi,
  createTicketApi,
  updateTicketApi,
  resolveTicketApi,
} from "../../api/helpdesk";

const mockFetch = vi.mocked(fetchTicketApi);
const mockCreate = vi.mocked(createTicketApi);
const mockUpdate = vi.mocked(updateTicketApi);
const mockResolve = vi.mocked(resolveTicketApi);

const sample = {
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
  status: "in_progress",
  resolved_at: null,
  sla_breached: false,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/helpdesk/tickets/new"]}>
      <Routes>
        <Route path="/helpdesk/tickets/new" element={<TicketFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/helpdesk/tickets/${id}/edit`]}>
      <Routes>
        <Route
          path="/helpdesk/tickets/:id/edit"
          element={<TicketFormPage />}
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe("TicketFormPage", () => {
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

  it("shows New Ticket heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new ticket/i)).toBeInTheDocument();
    });
  });

  it("pre-fills title when editing", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Login broken")).toBeInTheDocument();
    });
  });

  it("calls createTicketApi on new submit", async () => {
    mockCreate.mockResolvedValueOnce(sample);
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: "New issue" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockCreate).toHaveBeenCalled();
    });
  });

  it("calls updateTicketApi on edit submit", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockUpdate.mockResolvedValueOnce(sample);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Login broken")).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(mockUpdate).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("calls resolveTicketApi on Resolve click", async () => {
    mockFetch.mockResolvedValueOnce(sample);
    mockResolve.mockResolvedValueOnce({ ...sample, status: "resolved" });
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /resolve/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /resolve/i }));
    await waitFor(() => {
      expect(mockResolve).toHaveBeenCalledWith(1);
    });
  });
});
