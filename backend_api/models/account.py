# backend_api/models/account.py
from django.db import models
from .user import User

class Account(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="accounts",
        help_text="The user who owns this account."
    )
    name = models.CharField(max_length=255)
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "name")

    @property
    def balance(self):
        incomes_sum = self.incomes.aggregate(total=models.Sum('amount'))['total'] or 0
        expenses_sum = self.expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        return self.initial_balance + incomes_sum - expenses_sum

    def __str__(self):
        return self.name
