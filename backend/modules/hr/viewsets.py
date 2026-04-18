from rest_framework import viewsets

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.hr.models import Department, Employee, LeaveRequest, Payroll
from modules.hr.serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    LeaveRequestSerializer,
    PayrollSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """CRUD for departments within the authenticated user's company."""

    serializer_class = DepartmentSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Department.objects.order_by("name")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class EmployeeViewSet(viewsets.ModelViewSet):
    """CRUD for employees within the authenticated user's company."""

    serializer_class = EmployeeSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Employee.objects.select_related("department").order_by("last_name", "first_name")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """CRUD for leave requests within the authenticated user's company."""

    serializer_class = LeaveRequestSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = LeaveRequest.objects.select_related("employee").order_by("-start_date")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class PayrollViewSet(viewsets.ModelViewSet):
    """CRUD for payroll records within the authenticated user's company."""

    serializer_class = PayrollSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = Payroll.objects.select_related("employee").order_by("-period_start")

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
