import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useConfigStore } from "../../stores/configStore";
import EventFormPage from "./EventFormPage";

vi.mock("../../api/calendar", () => ({
  fetchEventApi: vi.fn(),
  createEventApi: vi.fn(),
  updateEventApi: vi.fn(),
}));

vi.mock("../../api/config", () => ({
  fetchModulesApi: vi.fn().mockResolvedValue([]),
  fetchModuleConfigApi: vi.fn(),
}));

import { fetchEventApi, createEventApi, updateEventApi } from "../../api/calendar";

const mockFetchEvent = vi.mocked(fetchEventApi);
const mockCreateEvent = vi.mocked(createEventApi);
const mockUpdateEvent = vi.mocked(updateEventApi);

const now = "2026-04-14T10:00:00Z";
const sampleEvent = {
  id: 1,
  title: "Board Meeting",
  description: "Q2 review",
  start_datetime: now,
  end_datetime: "2026-04-14T11:00:00Z",
  event_type: "meeting",
  status: "confirmed",
  location: "Board Room",
  all_day: false,
  is_recurring: false,
  recurrence_rule: "",
  external_uid: null,
  attendee_count: 5,
  created_at: now,
  updated_at: now,
};

function renderNewForm() {
  return render(
    <MemoryRouter initialEntries={["/calendar/events/new"]}>
      <Routes>
        <Route path="/calendar/events/new" element={<EventFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

function renderEditForm(id = 1) {
  return render(
    <MemoryRouter initialEntries={[`/calendar/events/${id}/edit`]}>
      <Routes>
        <Route path="/calendar/events/:id/edit" element={<EventFormPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("EventFormPage", () => {
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

  it("renders form heading for new event", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading")).toBeInTheDocument();
    });
  });

  it("shows New Event heading on create route", async () => {
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByText(/new event/i)).toBeInTheDocument();
    });
  });

  it("shows Edit Event heading on edit route", async () => {
    mockFetchEvent.mockResolvedValueOnce(sampleEvent);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByText(/edit event/i)).toBeInTheDocument();
    });
  });

  it("pre-fills form fields when editing", async () => {
    mockFetchEvent.mockResolvedValueOnce(sampleEvent);
    renderEditForm();
    await waitFor(() => {
      expect(screen.getByDisplayValue("Board Meeting")).toBeInTheDocument();
      expect(screen.getByDisplayValue("Board Room")).toBeInTheDocument();
    });
  });

  it("calls createEventApi on submit for new event", async () => {
    mockCreateEvent.mockResolvedValueOnce(sampleEvent);
    renderNewForm();

    await waitFor(() => {
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    });

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: "New Event Title" },
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockCreateEvent).toHaveBeenCalled();
    });
  });

  it("calls updateEventApi on submit for existing event", async () => {
    mockFetchEvent.mockResolvedValueOnce(sampleEvent);
    mockUpdateEvent.mockResolvedValueOnce(sampleEvent);
    renderEditForm();

    await waitFor(() => {
      expect(screen.getByDisplayValue("Board Meeting")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    await waitFor(() => {
      expect(mockUpdateEvent).toHaveBeenCalledWith(1, expect.any(Object));
    });
  });

  it("uses terminology for form label", async () => {
    useConfigStore.setState({ terminology: { Event: "Workshop" } });
    renderNewForm();
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /workshop/i })).toBeInTheDocument();
    });
  });
});
