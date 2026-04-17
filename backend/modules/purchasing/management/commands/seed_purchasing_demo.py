from core.management.commands._seed_helpers import SeedCommandBase
from modules.purchasing.models import PurchaseOrder, Vendor


class Command(SeedCommandBase):
    help = "Seed demo vendors + purchase orders for a company."

    def seed(self, company, *, reset: bool) -> int:
        if reset:
            PurchaseOrder.objects.filter(company=company).delete()
            Vendor.objects.filter(company=company).delete()

        vendor_specs = [
            ("Demo Supplier Co.", "orders@demo-supplier.test", "net_30"),
            ("Demo Logistics Ltd.", "info@demo-logistics.test", "net_60"),
        ]
        for name, email, terms in vendor_specs:
            Vendor.objects.get_or_create(
                company=company,
                name=name,
                defaults={"email": email, "payment_terms": terms},
            )

        vendor = Vendor.objects.filter(company=company).first()
        po_specs = [
            ("DEMO-PO-1", "draft"),
            ("DEMO-PO-2", "confirmed"),
        ]
        for number, status in po_specs:
            PurchaseOrder.objects.get_or_create(
                company=company,
                po_number=number,
                defaults={"vendor": vendor, "status": status},
            )
        return len(vendor_specs) + len(po_specs)
