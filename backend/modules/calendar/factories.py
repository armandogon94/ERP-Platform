import factory
from django.utils import timezone

from core.factories import CompanyFactory
from modules.calendar.models import Event, EventAttendee, Reminder, Resource


class ResourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Resource
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Resource {n}")
    resource_type = Resource.ResourceType.ROOM
    capacity = 1
    description = ""


class EventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Event
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f"Event {n}")
    description = ""
    start_datetime = factory.LazyFunction(timezone.now)
    end_datetime = factory.LazyAttribute(
        lambda o: o.start_datetime + timezone.timedelta(hours=1)
    )
    event_type = Event.EventType.MEETING
    status = Event.Status.CONFIRMED
    location = ""
    all_day = False
    is_recurring = False
    external_uid = None


class EventAttendeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventAttendee
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    event = factory.SubFactory(EventFactory, company=factory.SelfAttribute("..company"))
    email = factory.Sequence(lambda n: f"attendee{n}@example.com")
    response_status = EventAttendee.ResponseStatus.NEEDS_ACTION


class ReminderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reminder
        skip_postgeneration_save = True

    company = factory.SubFactory(CompanyFactory)
    event = factory.SubFactory(EventFactory, company=factory.SelfAttribute("..company"))
    trigger_minutes_before = 15
    method = Reminder.Method.NOTIFICATION
