from datetime import datetime

from django.db import transaction
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

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class EventViewSet(viewsets.ModelViewSet):
    """CRUD + polling-sync surface for calendar events (Slice 18, D27)."""

    serializer_class = EventSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend, OrderingFilter]
    queryset = Event.objects.prefetch_related("attendees").order_by("start_datetime")

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

        raw_since = self.request.query_params.get("updated_since")
        if raw_since:
            updated_since = _parse_updated_at(raw_since)
            # REVIEW I-5: when the param is present but unparseable, 400
            # rather than silently returning the full set.
            if updated_since is None:
                from rest_framework.exceptions import ValidationError
                raise ValidationError(
                    {"updated_since": f"Unparseable ISO-8601 timestamp: {raw_since!r}"}
                )
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

        # REVIEW I-2: an upsert against an existing external_uid MUST carry
        # updated_at — otherwise the LWW compare is undefined and a stale
        # payload could silently overwrite newer stored data. Reject with
        # 400 so the caller notices and fixes their sync cursor.
        raw_updated = request.data.get("updated_at")
        if not raw_updated:
            return Response(
                {"updated_at": "Required on upsert against existing external_uid (last-write-wins)."},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        incoming_updated = _parse_updated_at(raw_updated)
        if incoming_updated is None:
            return Response(
                {"updated_at": f"Unparseable ISO-8601 timestamp: {raw_updated!r}"},
                status=http_status.HTTP_400_BAD_REQUEST,
            )
        # REVIEW C-10: tie on updated_at preserves the stored record. Use <=
        # so only a strictly newer payload wins the last-write-wins compare.
        if incoming_updated <= existing.updated_at:
            # Stored version wins.
            return Response(
                self.get_serializer(existing).data,
                status=http_status.HTTP_200_OK,
            )

        serializer = self.get_serializer(existing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=http_status.HTTP_200_OK)

    def get_throttles(self):
        # REVIEW S-8: scope-throttle only the bulk action (500 events × 60/min
        # per user is the upper bound). Other actions stay unthrottled.
        if self.action == "bulk":
            from rest_framework.throttling import ScopedRateThrottle

            class _BulkScope(ScopedRateThrottle):
                scope = "calendar-bulk"

            return [_BulkScope()]
        return super().get_throttles()

    # ─── Bulk upsert ───────────────────────────────────────────────
    @action(detail=False, methods=["post"])
    @transaction.atomic
    def bulk(self, request):
        """REVIEW I-1: wrap the batch in a single transaction so partial
        failures roll back the whole set. A per-payload save point would
        let successes persist even when the caller's overall intent failed;
        the documented semantics are all-or-nothing at the batch level."""
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
                # REVIEW I-2: an upsert without updated_at cannot compare
                # LWW — surface as a per-row error so the caller can fix
                # their batch rather than silently overwriting stored data.
                raw_updated = item.get("updated_at")
                if not raw_updated:
                    errors.append({
                        "index": i,
                        "errors": {
                            "updated_at": "Required on upsert against existing external_uid."
                        },
                    })
                    continue
                incoming_updated = _parse_updated_at(raw_updated)
                if incoming_updated is None:
                    errors.append({
                        "index": i,
                        "errors": {
                            "updated_at": f"Unparseable ISO-8601: {raw_updated!r}"
                        },
                    })
                    continue
                # REVIEW C-10: tie on updated_at preserves the stored record.
                if incoming_updated <= existing.updated_at:
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

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Reminder.objects.select_related("event")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
