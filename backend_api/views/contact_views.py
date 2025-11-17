from rest_framework import viewsets, status, filters
from backend_api.models import Contact
from backend_api.serializers import ContactSerializer
from rest_framework.permissions import IsAuthenticated
from backend_api.utils.response_utils import success_response, error_response


class ContactViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Contact model.
    - Only accessible to authenticated users.
    - Automatically filters contacts by the logged-in user.
    - Provides search and ordering functionality.
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'mobile', 'email', 'billing_city', 'billing_state','billing_country']
    ordering_fields = ['created_at', 'name']

    # def filter_queryset(self, queryset):
    #     search_query = self.request.query_params.get('search')
    #     if search_query:
    #         # Try exact name first
    #         exact_matches = queryset.filter(name__iexact=search_query)
    #         if exact_matches.exists():
    #             return exact_matches
    #         # Otherwise fallback to DRF's broader search
    #         queryset = super().filter_queryset(queryset)
    #     return queryset

    def get_queryset(self):
        """Return only contacts belonging to the logged-in user."""
        return Contact.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """Assign user automatically when creating."""
        serializer.save(user=self.request.user)

    # -------------------------------
    # GET /contacts/
    # -------------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Contacts fetched successfully.", serializer.data)

    # -------------------------------
    # GET /contacts/<id>/
    # -------------------------------
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response("Contact retrieved successfully.", serializer.data)

    # -------------------------------
    # POST /contacts/
    # -------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return success_response("Contact created successfully.", serializer.data, status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # PUT /contacts/<id>/
    # PATCH /contacts/<id>/
    # -------------------------------
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return success_response("Contact updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # -------------------------------
    # DELETE /contacts/<id>/
    # -------------------------------
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response("Contact deleted successfully.", {}, status.HTTP_204_NO_CONTENT)
