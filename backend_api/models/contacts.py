# backend_api/models/contacts.py
from django.db import models
from django.utils.translation.template import blankout

from .user import User

class Contact(models.Model):
    # 🔗 Relationship
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="The user who owns this contact."
    )

    # 👤 Basic Details
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, help_text="Include country code if applicable.")
    email = models.EmailField(blank=True, null=True)

    # 🧾 Tax Identifiers (Optional)
    pan = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Permanent Account Number (optional, 10 characters)."
    )
    gst = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="GSTIN (optional, 15 characters)."
    )

    # 🏠 Address Details
    billing_address = models.TextField(blank=True, help_text="Billing address for this contact.")
    shipping_address = models.TextField(blank=True, help_text="Shipping address for this contact.")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    pincode = models.CharField(max_length=20, blank=True)

    # 🗒️ Miscellaneous
    notes = models.TextField(blank=True, help_text="Any additional notes about this contact.")

    # 🕒 Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ⚙️ Meta Info
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        unique_together = ('user', 'mobile')  # prevent duplicates for the same user

    # 📘 String Representation
    def __str__(self):
        return f"{self.name} ({self.mobile})"