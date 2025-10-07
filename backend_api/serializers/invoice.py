from rest_framework import serializers
from backend_api.models import InvoiceItem,Invoice
class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'rate', 'discount']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['contact', 'supply_type', 'invoice_date', 'items']

    def validate_contact(self, contact):
        user = self.context['request'].user
        if contact.user != user:
            raise serializers.ValidationError("You can only create invoices for your own contacts.")
        return contact

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        invoice = Invoice.objects.create(user=user, **validated_data)

        total_amount = 0
        for item_data in items_data:
            quantity = item_data['quantity']
            rate = item_data['rate']
            discount = item_data.get('discount', 0)

            total = (quantity * rate) - discount
            total_amount += total

            InvoiceItem.objects.create(
                invoice=invoice,
                total=total,
                **item_data
            )

        invoice.total_amount = total_amount
        invoice.save()

        return invoice
