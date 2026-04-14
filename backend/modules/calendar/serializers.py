from rest_framework import serializers

from modules.calendar.models import Event, EventAttendee, Reminder, Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id",
            "name",
            "resource_type",
            "capacity",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventSerializer(serializers.ModelSerializer):
    attendee_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "start_datetime",
            "end_datetime",
            "event_type",
            "status",
            "location",
            "all_day",
            "is_recurring",
            "recurrence_rule",
            "external_uid",
            "attendee_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "attendee_count", "created_at", "updated_at"]

    def get_attendee_count(self, obj) -> int:
        return obj.attendees.count()


class EventAttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAttendee
        fields = [
            "id",
            "event",
            "user",
            "resource",
            "email",
            "response_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = [
            "id",
            "event",
            "trigger_minutes_before",
            "method",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
