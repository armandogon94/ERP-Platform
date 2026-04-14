from rest_framework import serializers

from modules.hr.models import Department, Employee, LeaveRequest, Payroll


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_number",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "department",
            "department_name",
            "job_title",
            "hire_date",
            "status",
            "employee_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "full_name", "department_name", "created_at", "updated_at"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "employee_name",
            "leave_type",
            "start_date",
            "end_date",
            "days_requested",
            "status",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee_name", "created_at", "updated_at"]


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)

    class Meta:
        model = Payroll
        fields = [
            "id",
            "employee",
            "employee_name",
            "period_start",
            "period_end",
            "gross_amount",
            "net_amount",
            "status",
            "payment_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "employee_name", "created_at", "updated_at"]
