# backend_api/models/income.py
from django.db import models
from django.utils import timezone
from .user import User
from .account import Account

class Income(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="incomes"
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="incomes"
    )
    date = models.DateField(default=timezone.now)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"Income: {self.amount} ({self.category})"
