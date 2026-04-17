"""Projects module models: Project, Task, Milestone, ProjectTimesheet."""

from django.db import models

from core.models import TenantModel


class Project(TenantModel):
    """A project tracked by the organization."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, blank=True, default="")
    customer = models.ForeignKey(
        "core.Partner",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNED
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    description = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Task(TenantModel):
    """A work item on a project; supports subtasks via parent_task."""

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    assignee = models.ForeignKey(
        "hr.Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.TODO
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.NORMAL
    )
    due_date = models.DateField(null=True, blank=True)
    parent_task = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )

    class Meta(TenantModel.Meta):
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Milestone(TenantModel):
    """A significant checkpoint on a project."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    name = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta(TenantModel.Meta):
        ordering = ["due_date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.project.name} — {self.name}"


class ProjectTimesheet(TenantModel):
    """Hours logged against a project (and optionally a specific task)."""

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="timesheets"
    )
    task = models.ForeignKey(
        Task,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="timesheets",
    )
    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.PROTECT,
        related_name="+",
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    billable = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="")

    class Meta(TenantModel.Meta):
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.project.name} — {self.date} — {self.hours}h"
