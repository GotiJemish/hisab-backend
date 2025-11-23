from django.db import models
from django.utils import timezone
from .user import User
from .contacts import Contact
from .invoice_item import InvoiceItem

class Invoice(models.Model):
    bill_id = models.CharField(max_length=30, unique=True, editable=False)
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

    invoice_date = models.DateField(default=timezone.now)

    # ✔ Multi-items in one invoice
    items = models.ManyToManyField(InvoiceItem, related_name="invoice_items", blank=True)

    # Amount Summary
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Notes
    internal_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # auto-generate bill_id on create
        if not self.bill_id:
            today = timezone.now().date()
            today_str = today.strftime('%Y%m%d')

            count_today = Invoice.objects.filter(
                user=self.user,
                created_at__date=today
            ).count() + 1

            self.bill_id = f"INV{today_str}-{count_today:04d}"

        super().save(*args, **kwargs)

        # After saving invoice → update total amount from child items
        self.update_total()

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