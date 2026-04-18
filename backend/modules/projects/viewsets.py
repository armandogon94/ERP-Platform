from decimal import Decimal

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.mixins import FilterParamsMixin
from api.v1.permissions import IsCompanyMember
from modules.projects.models import Milestone, Project, ProjectTimesheet, Task
from modules.projects.serializers import (
    MilestoneSerializer,
    ProjectProgressSerializer,
    ProjectSerializer,
    ProjectTimesheetSerializer,
    TaskSerializer,
)


class ProjectViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Project.objects.select_related("customer").all()
    filter_params = {"status": "status", "customer": "customer_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        project = self.get_object()
        total = project.tasks.count()
        done = project.tasks.filter(status=Task.Status.DONE).count()
        hours = project.timesheets.aggregate(total=Sum("hours"))["total"] or Decimal(
            "0.00"
        )
        if project.budget and project.budget > 0:
            # Rough estimate: hours at a default $50/hr for demo; real pricing
            # belongs in Accounting. Here we just compare logged hours' value
            # (hours * 50) against budget.
            consumed = float((hours * Decimal("50.00")) / project.budget * 100)
        else:
            consumed = 0.0
        data = {
            "total_tasks": total,
            "done": done,
            "hours_logged": hours,
            "budget_consumed_pct": round(consumed, 2),
        }
        return Response(ProjectProgressSerializer(data).data)


class TaskViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Task.objects.select_related("project", "assignee").all()
    filter_params = {
        "status": "status",
        "project": "project_id",
        "assignee": "assignee_id",
    }

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class MilestoneViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = MilestoneSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Milestone.objects.select_related("project").all()
    filter_params = {"project": "project_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class ProjectTimesheetViewSet(FilterParamsMixin, viewsets.ModelViewSet):
    serializer_class = ProjectTimesheetSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ProjectTimesheet.objects.select_related(
        "project", "task", "employee"
    ).all()
    filter_params = {"project": "project_id", "employee": "employee_id"}

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
