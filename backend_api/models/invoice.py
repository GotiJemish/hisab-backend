import uuid
from django.db import models
from .user import User
from .contacts import Contact  # Assuming Contact model is already created
from django.utils import timezone



# def generate_unique_bill_id():
#     return uuid.uuid4().hex[:10].upper()  # 10-char uppercase unique string




class Invoice(models.Model):
    bill_id = models.CharField(max_length=30, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='invoices')
    supply_type = models.CharField(max_length=50)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.bill_id:
            today = timezone.now().date()
            today_str = today.strftime('%Y%m%d')

            # Count how many invoices this user has created today
            count_today = Invoice.objects.filter(
                user=self.user,
                created_at__date=today
            ).count() + 1

            self.bill_id = f"INV{today_str}-{count_today:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.bill_id} for {self.contact.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate total = (quantity * rate) - discount
        self.total = (self.quantity * self.rate) - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x {self.quantity}"
