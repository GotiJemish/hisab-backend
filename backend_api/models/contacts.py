# backend_api/models/contacts.py
from django.db import models

from .user import User


class Contact(models.Model):
    # 🔗 Relationship
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="contacts",
        help_text="The user who owns this contact.",
    )

    # 👤 Basic Details
    name = models.CharField(max_length=100)
    mobile = models.CharField(
        max_length=15, blank=True, null=True, help_text="Include country code if applicable."
    )
    email = models.EmailField(blank=True, null=True)

    # 🧾 Tax Identifiers (Optional)
    pan = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Permanent Account Number (optional, 10 characters).",
    )
    gst = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="GSTIN (optional, 15 characters).",
    )
    # 🏠 Billing Address
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_pincode = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    # 📦 Shipping Address
    same_as_billing = models.BooleanField(default=False)
    shipping_address = models.TextField(blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_pincode = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)

    # 💰 Payment
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    PAYMENT_TYPE_CHOICES = [
        ("receivable", "Receivable"),
        ("payable", "Payable"),
    ]
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE_CHOICES, default="receivable"
    )

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
    ]
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    # 🗒️ Miscellaneous
    notes = models.TextField(
        blank=True, help_text="Any additional notes about this contact."
    )

    # 🕒 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ⚙️ Meta Info
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        # We can't strictly enforce unique_together on user and mobile if mobile can be null,
        # but django handles nulls in unique_together by allowing multiple nulls depending on DB.
        unique_together = ("user", "mobile", "email")

    # 📘 String Representation
    def __str__(self):
        return f"{self.name} ({self.mobile or self.email})"

    def save(self, *args, **kwargs):
        if not self.mobile and not self.email:
            from django.core.exceptions import ValidationError
            raise ValidationError("Either mobile or email is required for a contact.")

        if self.same_as_billing:
            self.shipping_address = self.billing_address
            self.shipping_city = self.billing_city
            self.shipping_state = self.billing_state
            self.shipping_pincode = self.billing_pincode

        super().save(*args, **kwargs)
