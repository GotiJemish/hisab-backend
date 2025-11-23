# # backend_api/serializers/invoice.py
# from rest_framework import serializers
# from backend_api.models import InvoiceItem, Invoice
#
#
# # ✅ Standard response mixin (same as used earlier)
# class StandardResponseMixin:
#     def get_success_response(self, message, data=None):
#         return {
#             "status": "success",
#             "message": message,
#             "data": data or {}
#         }
#
#     def get_error_response(self, message, errors=None):
#         return {
#             "status": "error",
#             "message": message,
#             "errors": errors or {}
#         }
#
#
# # ✅ Invoice Item Serializer
# class InvoiceItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InvoiceItem
#         fields = ['description', 'quantity', 'rate', 'discount']
#
#
# # ✅ Invoice Serializer (main)
# class InvoiceSerializer(StandardResponseMixin, serializers.ModelSerializer):
#     items = InvoiceItemSerializer(many=True)
#
#     class Meta:
#         model = Invoice
#         fields = ['contact', 'supply_type', 'invoice_date', 'items']
#
#     # Ensure the contact belongs to the current user
#     def validate_contact(self, contact):
#         user = self.context['request'].user
#         if contact.user != user:
#             raise serializers.ValidationError(
#                 self.get_error_response(
#                     message="You can only create invoices for your own contacts.",
#                     errors={"contact": ["Invalid contact ownership."]}
#                 )
#             )
#         return contact
#
#     # Create invoice with nested items
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         user = self.context['request'].user
#
#         # Create invoice
#         invoice = Invoice.objects.create(user=user, **validated_data)
#
#         total_amount = 0
#         created_items = []
#
#         for item_data in items_data:
#             quantity = item_data['quantity']
#             rate = item_data['rate']
#             discount = item_data.get('discount', 0)
#
#             total = (quantity * rate) - discount
#             total_amount += total
#
#             # Create invoice item
#             item = InvoiceItem.objects.create(
#                 invoice=invoice,
#                 total=total,
#                 **item_data
#             )
#             created_items.append({
#                 "description": item.description,
#                 "quantity": item.quantity,
#                 "rate": item.rate,
#                 "discount": item.discount,
#                 "total": total
#             })
#
#         invoice.total_amount = total_amount
#         invoice.save()
#
#         return self.get_success_response(
#             message="Invoice created successfully.",
#             data={
#                 "invoice_id": invoice.id,
#                 "total_amount": total_amount,
#                 "items": created_items
#             }
#         )
