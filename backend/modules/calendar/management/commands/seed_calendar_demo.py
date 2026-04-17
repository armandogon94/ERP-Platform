from datetime import timedelta

from django.utils import timezone

from core.management.commands._seed_helpers import SeedCommandBase
from modules.calendar.models import Event


class Command(SeedCommandBase):
    help = "Seed demo calendar events for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Event.objects.filter(company=company).delete()

        now = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        seeds = [
            ("Demo onboarding meeting", now + timedelta(days=1), "meeting"),
            ("Demo team standup", now + timedelta(days=2), "meeting"),
            ("Demo customer appointment", now + timedelta(days=3), "appointment"),
        ]
        created = 0
        for title, start, event_type in seeds:
            _, was_new = Event.objects.get_or_create(
                company=company,
                title=title,
                defaults={
                    "start_datetime": start,
                    "end_datetime": start + timedelta(hours=1),
                    "event_type": event_type,
                },
            )
            if was_new:
                created += 1
        return created
