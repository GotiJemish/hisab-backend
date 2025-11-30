from django.db import models

class InvoiceItem(models.Model):
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)  # optional


    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.rate) - self.discount
        if self.total < 0:
            self.total = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x {self.quantity}"
