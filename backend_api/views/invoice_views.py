
# backend_api/views/invoice_views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from backend_api.models import Invoice
from backend_api.serializers.invoice import InvoiceSerializer
from backend_api.utils.response_utils import success_response, error_response

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["bill_id", "invoice_number", "invoice_type", "notes"]
    filterset_fields = ["invoice_type", "supply_type", "invoice_date", "total_amount"]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).order_by("-created_at")


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            invoice = serializer.save()
            return success_response(
                "Invoice created successfully.",
                InvoiceSerializer(invoice).data,
                status.HTTP_201_CREATED
            )

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        invoices = self.get_queryset()
        serializer = self.get_serializer(invoices, many=True)
        return success_response("Invoices fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return success_response("Invoice details fetched successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            invoice = serializer.save()
            return success_response(
                "Invoice updated successfully.",
                InvoiceSerializer(invoice).data
            )

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice.delete()
        return success_response("Invoice deleted successfully.", {}, status.HTTP_204_NO_CONTENT)
