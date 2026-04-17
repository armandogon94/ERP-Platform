import datetime
from decimal import Decimal

from core.management.commands._seed_helpers import SeedCommandBase
from modules.projects.models import Milestone, Project, Task


class Command(SeedCommandBase):
    help = "Seed demo project + tasks + milestones for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Task.objects.filter(company=company).delete()
            Milestone.objects.filter(company=company).delete()
            Project.objects.filter(company=company).delete()

        project, _ = Project.objects.get_or_create(
            company=company,
            code="DEMO-PRJ-1",
            defaults={
                "name": "Demo Project",
                "status": "active",
                "budget": Decimal("100000.00"),
                "start_date": datetime.date(2026, 1, 1),
            },
        )
        task_specs = [
            ("Plan phase", "done"),
            ("Build phase", "in_progress"),
            ("Launch phase", "todo"),
        ]
        for name, status in task_specs:
            Task.objects.get_or_create(
                company=company,
                project=project,
                name=name,
                defaults={"status": status},
            )
        Milestone.objects.get_or_create(
            company=company,
            project=project,
            name="Phase 1 complete",
            defaults={"due_date": datetime.date(2026, 6, 30)},
        )
        return 1 + len(task_specs) + 1
