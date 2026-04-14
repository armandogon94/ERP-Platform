import apiClient from "./client";

export interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  start_datetime: string;
  end_datetime: string;
  event_type: string;
  status: string;
  location: string;
  all_day: boolean;
  is_recurring: boolean;
  recurrence_rule: string;
  external_uid: string | null;
  attendee_count: number;
  created_at: string;
  updated_at: string;
}

export interface CalendarResource {
  id: number;
  name: string;
  resource_type: string;
  capacity: number;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface EventFilters {
  status?: string;
  event_type?: string;
  start?: string;
  end?: string;
  updated_since?: string;
}

export async function fetchEventsApi(
  filters?: EventFilters,
): Promise<CalendarEvent[]> {
  const { data } = await apiClient.get<CalendarEvent[]>(
    "/v1/calendar/events/",
    { params: filters },
  );
  return data;
}

export async function fetchEventApi(id: number): Promise<CalendarEvent> {
  const { data } = await apiClient.get<CalendarEvent>(
    `/v1/calendar/events/${id}/`,
  );
  return data;
}

export async function createEventApi(
  payload: Partial<CalendarEvent>,
): Promise<CalendarEvent> {
  const { data } = await apiClient.post<CalendarEvent>(
    "/v1/calendar/events/",
    payload,
  );
  return data;
}

export async function updateEventApi(
  id: number,
  payload: Partial<CalendarEvent>,
): Promise<CalendarEvent> {
  const { data } = await apiClient.patch<CalendarEvent>(
    `/v1/calendar/events/${id}/`,
    payload,
  );
  return data;
}

export async function deleteEventApi(id: number): Promise<void> {
  await apiClient.delete(`/v1/calendar/events/${id}/`);
}

export async function fetchResourcesApi(): Promise<CalendarResource[]> {
  const { data } = await apiClient.get<CalendarResource[]>(
    "/v1/calendar/resources/",
  );
  return data;
}
