# backend_api/serializers/invoice.py
from rest_framework import serializers
from backend_api.models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["id", "description", "quantity", "rate", "discount", "total"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            "id", "bill_id", "invoice_number", "contact", "invoice_type",
            "supply_type", "invoice_date", "items", "total_amount", "notes", "internal_note"
        ]

    def validate_invoice_type(self, value):
        allowed = ["default", "delivery_challan", "proforma", "credit_note"]
        if value not in allowed:
            raise serializers.ValidationError("Invalid invoice type")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)

        # Create and attach InvoiceItems
        for item_data in items_data:
            item = InvoiceItem.objects.create(**item_data)
            invoice.items.add(item)

        invoice.update_total()  # recalc total_amount
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.clear()
            for item_data in items_data:
                item = InvoiceItem.objects.create(**item_data)
                instance.items.add(item)
            instance.update_total()

        return instance






