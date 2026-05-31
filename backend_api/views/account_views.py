# backend_api/views/account_views.py

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from backend_api.models import Account, Income, Expense
from backend_api.utils.permissions import HasCompanyModulePermission
from backend_api.serializers import AccountSerializer, IncomeSerializer, ExpenseSerializer
from backend_api.utils.response_utils import success_response, error_response


class AccountViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Accounts.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, HasCompanyModulePermission]
    permission_module_name = "accounts"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Account.objects.filter(user__company=user.company).order_by("-created_at")
        return Account.objects.filter(user=user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Account created successfully.", serializer.data, status.HTTP_201_CREATED
            )
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Accounts fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Account retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Account updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            "Account deleted successfully.", {}, status.HTTP_204_NO_CONTENT
        )


class IncomeViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Income transactions.
    """
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated, HasCompanyModulePermission]
    permission_module_name = "accounts"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["category", "notes", "account__name"]
    ordering_fields = ["date", "created_at", "amount"]

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Income.objects.filter(user__company=user.company).order_by("-date", "-created_at")
        return Income.objects.filter(user=user).order_by("-date", "-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Income transaction created successfully.", serializer.data, status.HTTP_201_CREATED
            )
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Income transactions fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Income transaction retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Income transaction updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            "Income transaction deleted successfully.", {}, status.HTTP_204_NO_CONTENT
        )


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Expense transactions.
    """
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated, HasCompanyModulePermission]
    permission_module_name = "accounts"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["category", "notes", "account__name"]
    ordering_fields = ["date", "created_at", "amount"]

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Expense.objects.filter(user__company=user.company).order_by("-date", "-created_at")
        return Expense.objects.filter(user=user).order_by("-date", "-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                "Expense transaction created successfully.", serializer.data, status.HTTP_201_CREATED
            )
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Expense transactions fetched successfully.", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Expense transaction retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return success_response("Expense transaction updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(
            "Expense transaction deleted successfully.", {}, status.HTTP_204_NO_CONTENT
        )
