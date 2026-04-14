"""Tests for Calendar module models: Event, Resource."""
import pytest
from django.utils import timezone

from core.factories import CompanyFactory
from modules.calendar.factories import EventFactory, ResourceFactory
from modules.calendar.models import Event, Resource


@pytest.mark.django_db
class TestEventModel:
    def test_create_event(self):
        company = CompanyFactory()
        now = timezone.now()
        event = Event.objects.create(
            company=company,
            title="Team Meeting",
            start_datetime=now,
            end_datetime=now + timezone.timedelta(hours=1),
            event_type=Event.EventType.MEETING,
            status=Event.Status.CONFIRMED,
        )
        assert event.pk is not None
        assert event.title == "Team Meeting"
        assert event.company == company

    def test_event_str_contains_title(self):
        event = EventFactory(title="Dentist Appointment")
        assert "Dentist Appointment" in str(event)

    def test_event_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        EventFactory(company=c1, title="Event C1")
        EventFactory(company=c2, title="Event C2")
        assert Event.objects.filter(company=c1).count() == 1
        assert Event.objects.filter(company=c2).count() == 1

    def test_event_status_choices(self):
        event = EventFactory(status=Event.Status.TENTATIVE)
        assert event.status == Event.Status.TENTATIVE

    def test_event_type_appointment(self):
        event = EventFactory(event_type=Event.EventType.APPOINTMENT)
        assert event.event_type == Event.EventType.APPOINTMENT

    def test_event_type_shift(self):
        event = EventFactory(event_type=Event.EventType.SHIFT)
        assert event.event_type == Event.EventType.SHIFT

    def test_event_all_day_flag(self):
        event = EventFactory(all_day=True)
        assert event.all_day is True

    def test_event_external_uid_nullable(self):
        event = EventFactory(external_uid=None)
        assert event.external_uid is None

    def test_event_external_uid_unique(self):
        company = CompanyFactory()
        EventFactory(company=company, external_uid="crm-001")
        with pytest.raises(Exception):
            EventFactory(company=company, external_uid="crm-001")

    def test_event_factory_creates_valid_event(self):
        event = EventFactory()
        assert event.pk is not None
        assert event.start_datetime < event.end_datetime
        assert event.company is not None

    def test_event_soft_delete(self):
        event = EventFactory()
        event.soft_delete()
        assert Event.objects.filter(pk=event.pk).count() == 0
        assert Event.all_objects.filter(pk=event.pk).count() == 1


@pytest.mark.django_db
class TestResourceModel:
    def test_create_resource(self):
        company = CompanyFactory()
        resource = Resource.objects.create(
            company=company,
            name="Conference Room A",
            resource_type=Resource.ResourceType.ROOM,
            capacity=10,
        )
        assert resource.pk is not None
        assert resource.name == "Conference Room A"
        assert resource.capacity == 10

    def test_resource_str_contains_name(self):
        resource = ResourceFactory(name="Exam Chair 1")
        assert "Exam Chair 1" in str(resource)

    def test_resource_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ResourceFactory(company=c1, name="Room A")
        ResourceFactory(company=c2, name="Room B")
        assert Resource.objects.filter(company=c1).count() == 1
        assert Resource.objects.filter(company=c2).count() == 1

    def test_resource_type_choices(self):
        resource = ResourceFactory(resource_type=Resource.ResourceType.EQUIPMENT)
        assert resource.resource_type == Resource.ResourceType.EQUIPMENT

    def test_resource_factory_creates_valid_resource(self):
        resource = ResourceFactory()
        assert resource.pk is not None
        assert resource.company is not None

    def test_resource_capacity_default_is_one(self):
        resource = ResourceFactory()
        assert resource.capacity >= 1
