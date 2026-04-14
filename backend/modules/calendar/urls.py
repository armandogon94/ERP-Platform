from rest_framework.routers import DefaultRouter

from modules.calendar.viewsets import (
    EventAttendeeViewSet,
    EventViewSet,
    ReminderViewSet,
    ResourceViewSet,
)

router = DefaultRouter()
router.register("events", EventViewSet, basename="calendar-event")
router.register("resources", ResourceViewSet, basename="calendar-resource")
router.register("attendees", EventAttendeeViewSet, basename="calendar-attendee")
router.register("reminders", ReminderViewSet, basename="calendar-reminder")

urlpatterns = router.urls
