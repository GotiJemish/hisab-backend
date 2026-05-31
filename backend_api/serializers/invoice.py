# backend_api/serializers/invoice.py
from rest_framework import serializers
from backend_api.models import Invoice, InvoiceItem, Items
from backend_api.utils.invoice_utils import (
    get_missing_invoice_numbers,
    get_next_invoice_number,
    validate_user_invoice_number,
)


class InvoiceItemSerializer(serializers.ModelSerializer):
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Items.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "item_id",
            "description",
            "quantity",
            "rate",
            "discount",
            "tax",
            "gst_percentage",
            "tax_amount",
            "total",
            "delivery_challan_no",
        ]
        read_only_fields = ["total", "tax_amount"]

    def validate(self, data):
        """
        Auto-fill description & rate from Item if not provided
        """
        item = data.get("item_id")

        if item:
            data.setdefault("description", item.name)
            data.setdefault("rate", item.rate)

        # Default GST to 5% if not provided
        if "gst_percentage" not in data:
            data["gst_percentage"] = 5

        return data


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    available_invoice_numbers = serializers.SerializerMethodField()
    next_invoice_number = serializers.SerializerMethodField()
    gst_summary = serializers.SerializerMethodField()

    # invoice_date_display = serializers.SerializerMethodField()
    class Meta:
        model = Invoice
        fields = [
            "id",
            "bill_id",
            "invoice_number",
            "invoice_date",
            "contact",
            "invoice_type",
            "supply_type",
            "party_challan_no",
            "items",
            "total_amount",
            "internal_note",
            "notes",
            "available_invoice_numbers",
            "next_invoice_number",
            "gst_summary",
        ]
        read_only_fields = ["bill_id", "total_amount", "user"]

    # Return skipped/missing invoice numbers for UI dropdown
    def get_available_invoice_numbers(self, obj):
        return get_missing_invoice_numbers(obj.user, obj.invoice_date)

    # Return automatically generated next invoice number
    def get_next_invoice_number(self, obj):
        return get_next_invoice_number(obj.user, obj.invoice_date)

    def get_gst_summary(self, obj):
        """Calculate GST summary from all items."""
        from decimal import Decimal
        subtotal = Decimal('0')
        total_gst = Decimal('0')

        for item in obj.items.all():
            taxable = (item.quantity * item.rate) - item.discount
            if taxable < 0:
                taxable = Decimal('0')
            gst_rate = item.gst_percentage or Decimal('0')
            gst_amt = (taxable * gst_rate) / Decimal('100')
            subtotal += taxable
            total_gst += gst_amt

        return {
            "subtotal": str(subtotal),
            "total_gst": str(total_gst),
            "cgst": str(total_gst / 2),
            "sgst": str(total_gst / 2),
            "igst": str(total_gst),
            "grand_total": str(subtotal + total_gst),
        }

    # --------------------------
    # VALIDATION
    # --------------------------
    def validate(self, data):
        user = self.context["request"].user
        invoice_date = data.get("invoice_date")
        invoice_number = data.get("invoice_number")

        if invoice_number:
            try:
                validate_user_invoice_number(user, invoice_date, invoice_number)
            except Exception as e:
                raise serializers.ValidationError({"invoice_number": str(e)})

        return data

    # --------------------------
    # CREATE LOGIC
    # --------------------------
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        validated_data["user"] = self.context["request"].user
        user = self.context["request"].user
        validated_data["user"] = user
        invoice = Invoice.objects.create(**validated_data)
        # Create items
        for item_data in items_data:
            item = InvoiceItem(**item_data)
            item.save()
            invoice.items.add(item)

        invoice.update_total()
        invoice.refresh_from_db()
        return invoice

    # --------------------------
    # UPDATE LOGIC
    # --------------------------
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if items_data is not None:
            instance.items.clear()
            for item in items_data:
                item_obj = InvoiceItem.objects.create(**item)
                instance.items.add(item_obj)

        instance.update_total()
        return instance
