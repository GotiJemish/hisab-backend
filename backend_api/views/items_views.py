# backend_api/views/items_views.py

from rest_framework import viewsets, status, filters
from backend_api.models import Items

from rest_framework.permissions import IsAuthenticated

from backend_api.serializers import ItemSerializer
from backend_api.utils.response_utils import success_response, error_response


class ItemsViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for Items model.
    - Authenticated users only
    - Items belong to the logged-in user
    - Supports search & ordering
    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "type", "unit_type", "tax_category"]
    ordering_fields = ["created_at", "name", "rate"]

    # -----------------------------
    # QUERYSET RESTRICTION
    # -----------------------------
    def get_queryset(self):
        """Return only items belonging to the logged-in user."""
        return Items.objects.filter(user=self.request.user).order_by("-created_at")

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return success_response("Item created successfully.", serializer.data, status.HTTP_201_CREATED)

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    # -----------------------------
    # LIST
    # -----------------------------
    def list(self, request, *args, **kwargs):
        items = self.get_queryset()
        serializer = self.get_serializer(items, many=True)
        return success_response("Items fetched successfully.", serializer.data)

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.get_serializer(item)
        return success_response("Item retrieved successfully.", serializer.data)

    # -----------------------------
    # UPDATE / PATCH
    # -----------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return success_response("Item updated successfully.", serializer.data)

        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # -----------------------------
    # DELETE
    # -----------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response("Item deleted successfully.", {}, status.HTTP_204_NO_CONTENT)
