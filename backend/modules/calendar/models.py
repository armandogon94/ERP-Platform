"""Calendar module models: Event, Resource, EventAttendee, Reminder."""

from django.db import models

from core.models import TenantModel


class Resource(TenantModel):
    """A bookable resource — room, equipment, or person."""

    class ResourceType(models.TextChoices):
        ROOM = "room", "Room"
        EQUIPMENT = "equipment", "Equipment"
        PERSON = "person", "Person"

    name = models.CharField(max_length=200)
    resource_type = models.CharField(
        max_length=20,
        choices=ResourceType.choices,
        default=ResourceType.ROOM,
    )
    capacity = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_resource_type_display()})"


class Event(TenantModel):
    """A calendar event — appointment, meeting, booking, or shift."""

    class EventType(models.TextChoices):
        APPOINTMENT = "appointment", "Appointment"
        MEETING = "meeting", "Meeting"
        EVENT = "event", "Event"
        SHIFT = "shift", "Shift"

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        TENTATIVE = "tentative", "Tentative"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, default="")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.MEETING,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    location = models.CharField(max_length=300, blank=True, default="")
    all_day = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.TextField(blank=True, default="")

    # Optional link to CRM calendar for bidirectional sync
    external_uid = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="External UID from CRM calendar sync (RFC 5545 UID)",
    )

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self) -> str:
        return f"{self.title} ({self.start_datetime:%Y-%m-%d %H:%M})"


class EventAttendee(TenantModel):
    """A person or resource attending an event."""

    class ResponseStatus(models.TextChoices):
        NEEDS_ACTION = "needs_action", "Needs Action"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        TENTATIVE = "tentative", "Tentative"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="attendees",
    )
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_attendances",
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_attendances",
    )
    email = models.EmailField(blank=True, default="")
    response_status = models.CharField(
        max_length=20,
        choices=ResponseStatus.choices,
        default=ResponseStatus.NEEDS_ACTION,
    )

    class Meta:
        ordering = ["event", "email"]

    def __str__(self) -> str:
        label = self.email or (self.user.get_full_name() if self.user else "Unknown")
        return f"{label} @ {self.event.title}"


class Reminder(TenantModel):
    """A notification reminder for a calendar event."""

    class Method(models.TextChoices):
        EMAIL = "email", "Email"
        NOTIFICATION = "notification", "Notification"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reminders",
    )
    trigger_minutes_before = models.PositiveSmallIntegerField(default=15)
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.NOTIFICATION,
    )

    class Meta:
        ordering = ["trigger_minutes_before"]

    def __str__(self) -> str:
        return (
            f"{self.trigger_minutes_before}min before "
            f"'{self.event.title}' via {self.get_method_display()}"
        )
