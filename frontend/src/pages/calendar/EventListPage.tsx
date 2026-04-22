import { useEffect, useState } from "react";
import ListPageShell from "../../components/ListPageShell";
import { useTerminology } from "../../hooks/useTerminology";
import { type CalendarEvent, fetchEventsApi } from "../../api/calendar";

export default function EventListPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const eventLabel = useTerminology("Event", "Event");

  useEffect(() => {
    fetchEventsApi()
      .then((data) => {
        setEvents(data);
        setIsLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message || "Error loading events");
        setIsLoading(false);
      });
  }, []);

  return (
    <ListPageShell
      title={`${eventLabel}s`}
      isLoading={isLoading}
      error={error ? `Error: ${error}` : undefined}
      isEmpty={events.length === 0}
      empty={{ title: `No ${eventLabel.toLowerCase()}s yet` }}
    >
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Start</th>
            <th>End</th>
            <th>Type</th>
            <th>Status</th>
            <th>Attendees</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{event.title}</td>
              <td>{event.start_datetime}</td>
              <td>{event.end_datetime}</td>
              <td>{event.event_type}</td>
              <td>{event.status}</td>
              <td>{event.attendee_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </ListPageShell>
  );
}
