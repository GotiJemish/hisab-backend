# backend_api/models/items.py

from django.db import models
from .user import User


class Items(models.Model):

    # ---------- 🔗 Relationship ----------
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="The user who owns this item."
    )

    # ---------- 🏷️ Basic Details ----------
    name = models.CharField(max_length=100)

    ITEM_TYPE_CHOICES = [
        ("service", "Service"),
        ("product", "Product"),
        ("charge", "Charge"),
    ]
    type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        default="service"
    )

    sac = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    ITEM_MEASURE_CHOICES = [
        ("Bags", "Bags"),
        ("Bottl", "Bottle"),
        ("Box", "Box"),
        ("Carat", "Carat"),
        ("Cent", "Cent"),
        ("Cm", "Cm"),
        ("Dozen", "Dozen"),
        ("Feet", "Feet"),
        ("Gram", "Gram"),
        ("Hrs", "Hours"),
        ("Kg", "Kilogram"),
        ("Ltr", "Litre"),
        ("Mg", "Milligram"),
        ("Mlt", "Millilitre"),
        ("Mm", "Millimetre"),
        ("Mtr", "Metre"),
        ("Pcs", "Pieces"),
        ("Tblet", "Tablet"),
        ("Tonne", "Tonne"),
    ]

    unit_type = models.CharField(
        max_length=20,
        choices=ITEM_MEASURE_CHOICES,
        default="Pcs"
    )

    # ---------- 🧾 Tax Category ----------
    TAX_CATEGORY_CHOICES = [
        ("none", "None"),
        ("gst-0.25", "GST 0.25%"),
        ("gst-1", "GST 1%"),
        ("gst-3", "GST 3%"),
        ("gst-5", "GST 5%"),
        ("gst-12", "GST 12%"),
        ("gst-18", "GST 18%"),
        ("gst-28", "GST 28%"),
        ("nil-rated", "Nil Rated"),
        ("non-gst", "Non GST"),
        ("exempt", "Exempt"),
    ]

    tax_category = models.CharField(
        max_length=20,
        choices=TAX_CATEGORY_CHOICES,
        default="none"
    )

    invoice_description = models.TextField(blank=True)

    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    with_tax = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # ---------- 🕒 Timestamps ----------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------- ⚙️ Meta ----------
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Item"
        verbose_name_plural = "Items"
        unique_together = ('user', 'name')  # prevent duplicate names for same user

    # ---------- 📌 String Representation ----------
    def __str__(self):
        return self.name

    # ---------- 💾 Save Override ----------
    def save(self, *args, **kwargs):

        # Ensure required fields
        if not self.name:
            raise ValueError("Item name is required.")

        # Prevent negative values
        if self.rate < 0:
            raise ValueError("Rate cannot be negative.")

        if self.discount < 0:
            raise ValueError("Discount cannot be negative.")

        super().save(*args, **kwargs)
