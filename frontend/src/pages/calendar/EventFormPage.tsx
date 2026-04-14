import { type FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTerminology } from "../../hooks/useTerminology";
import {
  type CalendarEvent,
  createEventApi,
  fetchEventApi,
  updateEventApi,
} from "../../api/calendar";

interface FormState {
  title: string;
  description: string;
  start_datetime: string;
  end_datetime: string;
  event_type: string;
  status: string;
  location: string;
  all_day: boolean;
}

const EMPTY_FORM: FormState = {
  title: "",
  description: "",
  start_datetime: "",
  end_datetime: "",
  event_type: "meeting",
  status: "confirmed",
  location: "",
  all_day: false,
};

export default function EventFormPage() {
  const { id } = useParams<{ id?: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [isLoading, setIsLoading] = useState(isEdit);
  const [error, setError] = useState<string | null>(null);

  const eventLabel = useTerminology("Event", "Event");
  const headingPrefix = isEdit ? "Edit" : "New";

  useEffect(() => {
    if (!isEdit || !id) return;

    fetchEventApi(Number(id))
      .then((ev: CalendarEvent) => {
        setForm({
          title: ev.title,
          description: ev.description,
          start_datetime: ev.start_datetime,
          end_datetime: ev.end_datetime,
          event_type: ev.event_type,
          status: ev.status,
          location: ev.location,
          all_day: ev.all_day,
        });
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading event");
        setIsLoading(false);
      });
  }, [id, isEdit]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >,
  ) => {
    const { name, value, type } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      if (isEdit && id) {
        await updateEventApi(Number(id), form);
      } else {
        await createEventApi(form);
      }
      navigate("/calendar/events");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>
        {headingPrefix} {eventLabel}
      </h1>

      {error && <div role="alert">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="title">Title</label>
          <input
            id="title"
            name="title"
            value={form.title}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={form.description}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="start_datetime">Start</label>
          <input
            id="start_datetime"
            name="start_datetime"
            type="datetime-local"
            value={form.start_datetime}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="end_datetime">End</label>
          <input
            id="end_datetime"
            name="end_datetime"
            type="datetime-local"
            value={form.end_datetime}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="location">Location</label>
          <input
            id="location"
            name="location"
            value={form.location}
            onChange={handleChange}
          />
        </div>

        <div>
          <label htmlFor="event_type">Type</label>
          <select
            id="event_type"
            name="event_type"
            value={form.event_type}
            onChange={handleChange}
          >
            <option value="appointment">Appointment</option>
            <option value="meeting">Meeting</option>
            <option value="event">Event</option>
            <option value="shift">Shift</option>
          </select>
        </div>

        <div>
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={form.status}
            onChange={handleChange}
          >
            <option value="confirmed">Confirmed</option>
            <option value="tentative">Tentative</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <button type="submit">Save</button>
      </form>
    </div>
  );
}
