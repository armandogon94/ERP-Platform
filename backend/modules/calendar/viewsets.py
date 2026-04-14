from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.calendar.models import Event, EventAttendee, Reminder, Resource
from modules.calendar.serializers import (
    EventAttendeeSerializer,
    EventSerializer,
    ReminderSerializer,
    ResourceSerializer,
)


class ResourceViewSet(viewsets.ModelViewSet):
    """CRUD for bookable resources within the authenticated user's company."""

    serializer_class = ResourceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend, OrderingFilter]
    queryset = Resource.objects.order_by("name")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class EventViewSet(viewsets.ModelViewSet):
    """CRUD for calendar events with date-range and sync filtering."""

    serializer_class = EventSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend, OrderingFilter]
    queryset = Event.objects.prefetch_related("attendees").order_by("start_datetime")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    def get_queryset(self):
        qs = super().get_queryset()

        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)

        event_type = self.request.query_params.get("event_type")
        if event_type:
            qs = qs.filter(event_type=event_type)

        updated_since = self.request.query_params.get("updated_since")
        if updated_since:
            qs = qs.filter(updated_at__gte=updated_since)

        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            qs = qs.filter(end_datetime__gte=start)
        if end:
            qs = qs.filter(start_datetime__lte=end)

        return qs


class EventAttendeeViewSet(viewsets.ModelViewSet):
    """CRUD for event attendees within the authenticated user's company."""

    serializer_class = EventAttendeeSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = EventAttendee.objects.select_related("event", "user", "resource")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ReminderViewSet(viewsets.ModelViewSet):
    """CRUD for event reminders within the authenticated user's company."""

    serializer_class = ReminderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Reminder.objects.select_related("event")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
