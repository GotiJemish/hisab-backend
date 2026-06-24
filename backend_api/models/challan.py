from django.db import models
from django.utils import timezone
from .user import User
from .contacts import Contact
from .challan_item import ChallanItem


class Challan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="challans")
    # Party
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="challan_contact"
    )
    # Challan Settings
    invoice_type = models.CharField(
        max_length=20,
        choices=[
            ("default", "Default"),
            ("delivery_challan", "Delivery Challan"),
            ("old_dc", "OLD DC"),
        ],
        default="delivery_challan",
    )
    supply_type = models.CharField(
        max_length=30,
        default="regular",
        choices=[
            ("regular", "Regular"),
            ("bill_to_ship_to", "Bill To - Ship To"),
            ("bill_from_dispatch_from", "Bill From - Dispatch From"),
            ("a_party", "4 Party Transaction"),
        ],
    )
    bill_id = models.CharField(max_length=30, unique=True, blank=True)
    invoice_number = models.CharField(max_length=30, blank=True)

    invoice_date = models.DateField(default=timezone.now)

    # Multi-items in one challan
    items = models.ManyToManyField(
        ChallanItem, related_name="challan_items", blank=True
    )

    # Amount Summary
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Challan Numbers
    party_challan_no = models.CharField(max_length=50, blank=True, default="")

    # Notes
    internal_note = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_bill_id(self):
        today = timezone.now().date().strftime("%d%m%y")
        prefix = f"CHA{today}"

        last_challan = (
            Challan.objects.filter(bill_id__startswith=prefix)
            .order_by("-bill_id")
            .first()
        )

        if last_challan:
            last_number = int(last_challan.bill_id.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}-{new_number:04d}"

    def generate_invoice_number(self):
        today = timezone.now().date()
        prefix = today.strftime("%b").upper()
        yydd = today.strftime("%y%d")

        base = f"CH-{prefix}-{yydd}"

        last_challan = (
            Challan.objects.filter(invoice_number__startswith=base)
            .order_by("-invoice_number")
            .first()
        )

        if last_challan:
            last4 = int(last_challan.invoice_number[-4:])
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
        """Recalculate challan total from all items."""
        total = sum(item.total for item in self.items.all())
        if self.total_amount != total:
            self.total_amount = total
            super().save(update_fields=["total_amount"])

    def __str__(self):
        return f"Challan {self.bill_id}"
