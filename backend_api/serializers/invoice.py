# backend_api/serializers/invoice.py
from datetime import timezone
from datetime import datetime
from rest_framework import serializers
from backend_api.models import Invoice, InvoiceItem
from backend_api.utils.invoice_utils import get_missing_invoice_numbers, get_next_invoice_number


class InvoiceItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = InvoiceItem
        fields = ["id", "description", "quantity", "rate", "discount", "total"]
        read_only_fields = ["total"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    available_invoice_numbers = serializers.SerializerMethodField()
    next_invoice_number = serializers.SerializerMethodField()
    invoice_date_display = serializers.SerializerMethodField()
    class Meta:
        model = Invoice
        fields = [
            "id", "bill_id", "invoice_number", "invoice_date",
            "invoice_date_display",
            "user", "contact", "invoice_type", "supply_type",
            "items", "total_amount",
            "internal_note", "notes",
            "available_invoice_numbers", "next_invoice_number"
        ]
        read_only_fields = ["bill_id", "total_amount", "user"]

    # Return skipped/missing invoice numbers for UI dropdown
    def get_available_invoice_numbers(self, obj):
        return get_missing_invoice_numbers(obj.user, obj.invoice_date)

    # Return automatically generated next invoice number
    def get_next_invoice_number(self, obj):
        return get_next_invoice_number(obj.user, obj.invoice_date)


        # ----------------------------------
        # PARSE INPUT DATE (DD-MM-YYYY → YYYY-MM-DD)
        # ----------------------------------

    def to_internal_value(self, data):
        if "invoice_date" in data:
            date_str = data["invoice_date"]

            # Accept only dd-mm-yyyy
            try:
                parsed_date = datetime.strptime(date_str, "%d-%m-%Y").date()
                data["invoice_date"] = parsed_date
            except ValueError:
                raise serializers.ValidationError({
                    "invoice_date": "Date must be in DD-MM-YYYY format"
                })

        return super().to_internal_value(data)
        # ----------------------------------
        # FORMAT OUTPUT DATE (YYYY-MM-DD → DD-MM-YYYY)
        # ----------------------------------

    def to_representation(self, instance):
        response = super().to_representation(instance)

        # Convert format
        response["invoice_date"] = instance.invoice_date.strftime("%d-%m-%Y")
        return response

        # Display field for UI

    def get_invoice_date_display(self, obj):
        return obj.invoice_date.strftime("%d-%m-%Y")
    # --------------------------
    # VALIDATION
    # --------------------------
    # def validate(self, data):
    #     user = self.context["request"].user
    #     invoice_date = data.get("invoice_date", timezone.now().date())
    #     invoice_number = data.get("invoice_number")
    #
    #     if invoice_number:
    #         # Check user given invoice_number is valid
    #         validate_user_invoice_number(user, invoice_date, invoice_number)
    #
    #     return data

    # --------------------------
    # CREATE LOGIC
    # --------------------------
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user
        validated_data["user"] = user
        invoice = Invoice.objects.create(**validated_data)
        # Create items
        for item in items_data:
            item_obj = InvoiceItem.objects.create(**item)
            invoice.items.add(item_obj)

        invoice.update_total()
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


