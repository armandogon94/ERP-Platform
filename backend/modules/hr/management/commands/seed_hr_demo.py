from core.management.commands._seed_helpers import SeedCommandBase
from modules.hr.models import Department, Employee


class Command(SeedCommandBase):
    help = "Seed demo HR data (departments + employees) for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            Employee.objects.filter(company=company).delete()
            Department.objects.filter(company=company).delete()

        departments = ["Operations", "Finance", "Sales"]
        for name in departments:
            Department.objects.get_or_create(company=company, name=name)

        ops = Department.objects.get(company=company, name="Operations")
        fin = Department.objects.get(company=company, name="Finance")
        sales = Department.objects.get(company=company, name="Sales")

        seeds = [
            ("DEMO-001", "Alice", "Lane", "alice@demo.test", ops, "Manager"),
            ("DEMO-002", "Bob", "Reyes", "bob@demo.test", ops, "Analyst"),
            ("DEMO-003", "Carol", "Singh", "carol@demo.test", fin, "Accountant"),
            ("DEMO-004", "David", "Yoo", "david@demo.test", sales, "Sales Rep"),
        ]
        created = 0
        for number, first, last, email, dept, title in seeds:
            _, was_new = Employee.objects.get_or_create(
                company=company,
                employee_number=number,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "department": dept,
                    "job_title": title,
                },
            )
            if was_new:
                created += 1
        return created + len(departments)
