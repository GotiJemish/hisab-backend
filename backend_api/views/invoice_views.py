# backend_api/views/invoice_views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, status
from django.utils.dateparse import parse_date
from rest_framework.permissions import IsAuthenticated
from backend_api.utils.permissions import HasCompanyModulePermission
from backend_api.models import Invoice
from backend_api.serializers.invoice import InvoiceSerializer
from backend_api.utils.invoice_utils import (
    get_missing_invoice_numbers,
    get_next_invoice_number,
)
from backend_api.utils.response_utils import success_response, error_response


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, HasCompanyModulePermission]
    permission_module_name = "invoices"
    filter_backends = [SearchFilter, DjangoFilterBackend]
    # search_fields = ["bill_id", "invoice_number", "invoice_type", "notes"]
    # filterset_fields = ["invoice_type", "supply_type", "invoice_date", "total_amount"]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "bill_id",
        "invoice_number",
        "invoice_type",
        "notes",
        "contact__name",
    ]
    filterset_fields = ["invoice_type", "supply_type", "invoice_date", "total_amount"]

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Invoice.objects.filter(user__company=user.company).order_by("-created_at")
        return Invoice.objects.filter(user=user).order_by("-created_at")

    # ------------------------------------------------------
    # API: GET missing invoice numbers for selected date
    # ------------------------------------------------------
    @action(detail=False, methods=["GET"], url_path="invoice-number")
    def invoice_number(self, request):
        date_str = request.query_params.get("date")
        if not date_str:
            return error_response(
                {"error": "date is required"}, status.HTTP_400_BAD_REQUEST
            )

        # Let Django parse the date (YYYY-MM-DD or similar)
        parsed_date = parse_date(date_str)

        if not parsed_date:
            return error_response({"date": "Invalid date"}, status.HTTP_400_BAD_REQUEST)

        user = request.user

        missing = get_missing_invoice_numbers(user, parsed_date)
        next_number = get_next_invoice_number(user, parsed_date)

        return success_response(
            "Invoice numbers fetched successfully.",
            {"missing_numbers": missing, "next_invoice_number": next_number},
            status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            invoice = serializer.save()
            return success_response(
                "Invoice created successfully.",
                InvoiceSerializer(invoice).data,
                status.HTTP_201_CREATED,
            )

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Invoices fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        invoice = self.get_object()
        serializer = self.get_serializer(invoice)
        return success_response(
            "Invoice details fetched successfully.", serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            invoice = serializer.save()
            return success_response(
                "Invoice updated successfully.", InvoiceSerializer(invoice).data
            )

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        invoice = self.get_object()
        invoice.delete()
        return success_response(
            "Invoice deleted successfully.", {}, status.HTTP_204_NO_CONTENT
        )
