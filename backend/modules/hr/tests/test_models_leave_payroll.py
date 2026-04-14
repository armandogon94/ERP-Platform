"""Tests for LeaveRequest and Payroll models."""
import pytest
from decimal import Decimal
from django.utils import timezone

from core.factories import CompanyFactory
from modules.hr.factories import EmployeeFactory, LeaveRequestFactory, PayrollFactory
from modules.hr.models import Employee, LeaveRequest, Payroll


@pytest.mark.django_db
class TestLeaveRequestModel:
    def test_create_leave_request(self):
        employee = EmployeeFactory()
        lr = LeaveRequest.objects.create(
            company=employee.company,
            employee=employee,
            leave_type=LeaveRequest.LeaveType.ANNUAL,
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            days_requested=1,
            status=LeaveRequest.Status.PENDING,
        )
        assert lr.pk is not None
        assert lr.status == LeaveRequest.Status.PENDING

    def test_leave_request_str(self):
        lr = LeaveRequestFactory(leave_type=LeaveRequest.LeaveType.SICK)
        assert lr.employee.first_name in str(lr)

    def test_leave_request_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        LeaveRequestFactory(company=c1, employee=EmployeeFactory(company=c1))
        LeaveRequestFactory(company=c2, employee=EmployeeFactory(company=c2))
        assert LeaveRequest.objects.filter(company=c1).count() == 1
        assert LeaveRequest.objects.filter(company=c2).count() == 1

    def test_leave_request_status_transitions(self):
        lr = LeaveRequestFactory(status=LeaveRequest.Status.PENDING)
        lr.status = LeaveRequest.Status.APPROVED
        lr.save()
        lr.refresh_from_db()
        assert lr.status == LeaveRequest.Status.APPROVED

    def test_leave_request_all_leave_types(self):
        emp = EmployeeFactory()
        for leave_type, _ in LeaveRequest.LeaveType.choices:
            lr = LeaveRequestFactory(
                company=emp.company,
                employee=emp,
                leave_type=leave_type,
            )
            assert lr.leave_type == leave_type

    def test_leave_request_soft_delete(self):
        lr = LeaveRequestFactory()
        lr.soft_delete()
        assert LeaveRequest.objects.filter(pk=lr.pk).count() == 0
        assert LeaveRequest.all_objects.filter(pk=lr.pk).count() == 1


@pytest.mark.django_db
class TestPayrollModel:
    def test_create_payroll(self):
        emp = EmployeeFactory()
        today = timezone.now().date()
        p = Payroll.objects.create(
            company=emp.company,
            employee=emp,
            period_start=today.replace(day=1),
            period_end=today,
            gross_amount=Decimal("5000.00"),
            net_amount=Decimal("3800.00"),
            status=Payroll.Status.DRAFT,
        )
        assert p.pk is not None
        assert p.gross_amount == Decimal("5000.00")

    def test_payroll_str(self):
        p = PayrollFactory()
        assert p.employee.first_name in str(p)

    def test_payroll_unique_per_employee_period(self):
        emp = EmployeeFactory()
        today = timezone.now().date()
        Payroll.objects.create(
            company=emp.company,
            employee=emp,
            period_start=today.replace(day=1),
            period_end=today,
            gross_amount=Decimal("5000.00"),
            net_amount=Decimal("3800.00"),
        )
        with pytest.raises(Exception):
            Payroll.objects.create(
                company=emp.company,
                employee=emp,
                period_start=today.replace(day=1),
                period_end=today,
                gross_amount=Decimal("5000.00"),
                net_amount=Decimal("3800.00"),
            )

    def test_payroll_status_transitions(self):
        p = PayrollFactory(status=Payroll.Status.DRAFT)
        p.status = Payroll.Status.PROCESSED
        p.save()
        p.refresh_from_db()
        assert p.status == Payroll.Status.PROCESSED

    def test_payroll_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        e1, e2 = EmployeeFactory(company=c1), EmployeeFactory(company=c2)
        PayrollFactory(company=c1, employee=e1)
        PayrollFactory(company=c2, employee=e2)
        assert Payroll.objects.filter(company=c1).count() == 1
        assert Payroll.objects.filter(company=c2).count() == 1
