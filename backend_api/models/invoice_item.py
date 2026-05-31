from django.db import models


class InvoiceItem(models.Model):
    item_id = models.ForeignKey(
        "backend_api.Items", on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.ForeignKey("backend_api.Tax", on_delete=models.SET_NULL, null=True, blank=True)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_challan_no = models.CharField(max_length=50, blank=True, default="")

    def save(self, *args, **kwargs):
        from decimal import Decimal
        subtotal = (self.quantity * self.rate) - self.discount
        if subtotal < 0:
            subtotal = Decimal('0')

        # Calculate GST from gst_percentage field
        gst_rate = self.gst_percentage or Decimal('0')
        self.tax_amount = (subtotal * gst_rate) / Decimal('100')

        self.total = subtotal + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_id} x {self.quantity}"

