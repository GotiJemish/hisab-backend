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
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        subtotal = (self.quantity * self.rate) - self.discount
        if subtotal < 0:
            subtotal = 0
            
        # Calculate tax if tax is assigned
        if self.tax:
            self.tax_amount = (subtotal * self.tax.rate) / 100
        else:
            self.tax_amount = 0
            
        self.total = subtotal + self.tax_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_id} x {self.quantity}"
