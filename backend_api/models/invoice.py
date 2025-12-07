from uuid import uuid4

from django.db import models
from django.utils import timezone
from .user import User
from .contacts import Contact
from .invoice_item import InvoiceItem
from django.utils.crypto import get_random_string

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    # Party
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="invoice_contact")
    # Invoice Settings
    invoice_type = models.CharField(
        max_length=20,
        choices=[
            ('default', 'Default'),
            ('delivery_challan', 'Delivery Challan'),
            ('old_dc', 'OLD DC')
        ],
        default='default'  # ✅ Add default so old rows get a valid value
    )
    supply_type = models.CharField(
        max_length=30,
        default="regular",
        choices=[
            ('regular', 'Regular'),
            ('bill_to_ship_to', 'Bill To - Ship To'),
            ('bill_from_dispatch_from', 'Bill From - Dispatch From'),
            ('a_party', '4 Party Transaction'),
        ]
    )
    bill_id = models.CharField(max_length=30, unique=True, blank=True)
    invoice_number = models.CharField(max_length=30, unique=True, blank=True)

    invoice_date = models.DateField(default=timezone.now)

    # ✔ Multi-items in one invoice
    items = models.ManyToManyField(InvoiceItem, related_name="invoice_items", blank=True)

    # Amount Summary
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Notes
    internal_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_bill_id(self):
        today = timezone.now().date().strftime("%d%m%y")
        prefix = f"INV{today}"

        last_invoice = Invoice.objects.filter(
            bill_id__startswith=prefix
        ).order_by("-bill_id").first()

        if last_invoice:
            last_number = int(last_invoice.bill_id.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}-{new_number:04d}"

    def generate_invoice_number(self):
        today = timezone.now().date()
        prefix = today.strftime("%b").upper()
        yydd = today.strftime("%y%d")

        base = f"{prefix}-{yydd}"

        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=base
        ).order_by("-invoice_number").first()

        if last_invoice:
            last4 = int(last_invoice.invoice_number[-4:])
            new_last4 = last4 + 1
        else:
            new_last4 = 1

        return f"{base}{new_last4:04d}"


    def save(self, *args, **kwargs):
        if not self.bill_id:
            self.bill_id = self.generate_bill_id()

        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        super().save(*args, **kwargs)

    def update_total(self):
        """Recalculate invoice total from all items."""
        total = sum(item.total for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=["total_amount"])

    def __str__(self):
        return f"Invoice {self.bill_id}"


# {
#     "user": 1,
#     "contact": 12,
#     "invoice_type": "default",
#     "supply_type": "regular",
#     "items": [
#         {
#             "description": "Item 1",
#             "quantity": 5,
#             "rate": 120,
#             "discount": 10
#         },
#         {
#             "description": "Item 2",
#             "quantity": 2,
#             "rate": 500,
#             "discount": 0
#         }
#     ]
# }