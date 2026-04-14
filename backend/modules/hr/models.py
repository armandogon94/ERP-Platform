"""HR module models: Department, Employee, LeaveRequest, Payroll."""

from django.db import models

from core.models import TenantModel


class Department(TenantModel):
    """An organizational department within a company."""

    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ["company", "name"]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.company.slug})"


class Employee(TenantModel):
    """A person employed by a company.

    May optionally link to a Django User account for system access.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        TERMINATED = "terminated", "Terminated"
        ON_LEAVE = "on_leave", "On Leave"

    class EmployeeType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACTOR = "contractor", "Contractor"
        INTERN = "intern", "Intern"

    # Identity
    employee_number = models.CharField(max_length=50, blank=True, default="")
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()

    # Org structure
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )
    job_title = models.CharField(max_length=200, blank=True, default="")
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_reports",
    )

    # Employment details
    hire_date = models.DateField(null=True, blank=True)
    termination_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    employee_type = models.CharField(
        max_length=20,
        choices=EmployeeType.choices,
        default=EmployeeType.FULL_TIME,
    )

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class LeaveRequest(TenantModel):
    """A request for time off from an employee."""

    class LeaveType(models.TextChoices):
        ANNUAL = "annual", "Annual Leave"
        SICK = "sick", "Sick Leave"
        PERSONAL = "personal", "Personal Leave"
        MATERNITY = "maternity", "Maternity Leave"
        PATERNITY = "paternity", "Paternity Leave"
        UNPAID = "unpaid", "Unpaid Leave"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices,
        default=LeaveType.ANNUAL,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    days_requested = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    reason = models.TextField(blank=True, default="")
    approved_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_leaves",
    )

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return (
            f"{self.employee.full_name} — {self.get_leave_type_display()} "
            f"({self.start_date} to {self.end_date})"
        )


class Payroll(TenantModel):
    """A payroll record for an employee for a given period."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PROCESSED = "processed", "Processed"
        PAID = "paid", "Paid"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payrolls",
    )
    period_start = models.DateField()
    period_end = models.DateField()
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ["employee", "period_start", "period_end"]
        ordering = ["-period_start"]

    def __str__(self) -> str:
        return (
            f"{self.employee.full_name} payroll "
            f"{self.period_start} – {self.period_end}"
        )
