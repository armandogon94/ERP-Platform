from rest_framework import serializers

from modules.projects.models import Milestone, Project, ProjectTimesheet, Task
from api.v1.serializer_fields import TenantScopedSerializerMixin


class ProjectSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "code",
            "customer",
            "customer_name",
            "start_date",
            "end_date",
            "status",
            "budget",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "customer_name", "created_at", "updated_at"]


class TaskSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.full_name", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "assignee",
            "assignee_name",
            "status",
            "priority",
            "due_date",
            "parent_task",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project_name",
            "assignee_name",
            "created_at",
            "updated_at",
        ]


class MilestoneSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Milestone
        fields = [
            "id",
            "project",
            "project_name",
            "name",
            "due_date",
            "completed",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project_name",
            "created_at",
            "updated_at",
        ]


class ProjectTimesheetSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = ProjectTimesheet
        fields = [
            "id",
            "project",
            "project_name",
            "task",
            "employee",
            "employee_name",
            "date",
            "hours",
            "billable",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "project_name",
            "employee_name",
            "created_at",
            "updated_at",
        ]


class ProjectProgressSerializer(serializers.Serializer):
    """Read-only response for the /projects/{id}/progress/ action."""

    total_tasks = serializers.IntegerField()
    done = serializers.IntegerField()
    hours_logged = serializers.DecimalField(max_digits=14, decimal_places=2)
    budget_consumed_pct = serializers.FloatField()
