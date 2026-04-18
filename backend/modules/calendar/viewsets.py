from datetime import datetime

from django.utils.dateparse import parse_datetime
from rest_framework import status as http_status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.calendar.models import Event, EventAttendee, Reminder, Resource
from modules.calendar.serializers import (
    EventAttendeeSerializer,
    EventSerializer,
    ReminderSerializer,
    ResourceSerializer,
)


# Calendar-sync contract: see docs/CALENDAR-SYNC-POLLING.md
MAX_BULK_EVENTS = 500


def _parse_updated_at(raw: str | None) -> datetime | None:
    """Parse an ISO-8601 timestamp tolerating URL-quoted `+` as space."""
    if not raw:
        return None
    fixed = raw.replace(" ", "+")
    return parse_datetime(fixed)


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend, OrderingFilter]
    queryset = Resource.objects.order_by("name")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class EventViewSet(viewsets.ModelViewSet):
    """CRUD + polling-sync surface for calendar events (Slice 18, D27)."""

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

        updated_since = _parse_updated_at(
            self.request.query_params.get("updated_since")
        )
        if updated_since is not None:
            qs = qs.filter(updated_at__gte=updated_since)

        start = self.request.query_params.get("start")
        end = self.request.query_params.get("end")
        if start:
            qs = qs.filter(end_datetime__gte=start)
        if end:
            qs = qs.filter(start_datetime__lte=end)

        return qs

    # ─── Upsert via POST ────────────────────────────────────────────
    def create(self, request, *args, **kwargs):
        """Upsert an event by `external_uid` with last-write-wins on updated_at.

        * If `external_uid` is empty → behave like a normal create.
        * If an event with the same `external_uid` already exists for this
          company:
            - If the incoming payload's `updated_at` is older than the
              stored record's, return the stored record with 200.
            - Otherwise update the stored record (LWW win).
        """
        external_uid = request.data.get("external_uid")
        if not external_uid:
            return super().create(request, *args, **kwargs)

        existing = Event.objects.filter(
            company=request.company, external_uid=external_uid
        ).first()
        if existing is None:
            return super().create(request, *args, **kwargs)

        incoming_updated = _parse_updated_at(request.data.get("updated_at"))
        # REVIEW C-10: tie on updated_at preserves the stored record. Use <=
        # so only a strictly newer payload wins the last-write-wins compare.
        if incoming_updated is not None and incoming_updated <= existing.updated_at:
            # Stored version wins.
            return Response(
                self.get_serializer(existing).data,
                status=http_status.HTTP_200_OK,
            )

        serializer = self.get_serializer(existing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=http_status.HTTP_200_OK)

    # ─── Bulk upsert ───────────────────────────────────────────────
    @action(detail=False, methods=["post"])
    def bulk(self, request):
        payload = request.data
        if not isinstance(payload, list):
            return Response(
                {"detail": "Expected a JSON array of event payloads."},
                status=400,
            )
        if len(payload) > MAX_BULK_EVENTS:
            return Response(
                {
                    "detail": (
                        f"Bulk payload capped at {MAX_BULK_EVENTS} events; "
                        f"received {len(payload)}."
                    ),
                },
                status=400,
            )

        created = 0
        updated = 0
        skipped = 0
        errors: list[dict] = []

        for i, item in enumerate(payload):
            uid = item.get("external_uid")
            existing = None
            if uid:
                existing = Event.objects.filter(
                    company=request.company, external_uid=uid
                ).first()
            if existing is None:
                serializer = self.get_serializer(data=item)
                if not serializer.is_valid():
                    errors.append({"index": i, "errors": serializer.errors})
                    continue
                serializer.save(company=request.company)
                created += 1
            else:
                incoming_updated = _parse_updated_at(item.get("updated_at"))
                # REVIEW C-10: same LWW semantics as single upsert — tie
                # preserves stored record.
                if (
                    incoming_updated is not None
                    and incoming_updated <= existing.updated_at
                ):
                    skipped += 1
                    continue
                serializer = self.get_serializer(
                    existing, data=item, partial=True
                )
                if not serializer.is_valid():
                    errors.append({"index": i, "errors": serializer.errors})
                    continue
                serializer.save()
                updated += 1

        return Response(
            {
                "created": created,
                "updated": updated,
                "skipped": skipped,
                "errors": errors,
            }
        )


class EventAttendeeViewSet(viewsets.ModelViewSet):
    serializer_class = EventAttendeeSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = EventAttendee.objects.select_related("event", "user", "resource")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Reminder.objects.select_related("event")
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
