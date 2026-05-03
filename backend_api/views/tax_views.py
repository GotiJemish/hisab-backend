from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from backend_api.models.tax import Tax
from backend_api.serializers.tax import TaxSerializer
from backend_api.utils.response_utils import success_response, error_response

class TaxViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaxSerializer

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Tax.objects.filter(company=user.company).order_by('-created_at')
        return Tax.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Taxes retrieved successfully.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Tax created successfully.", serializer.data, status.HTTP_201_CREATED)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response("Tax updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response("Tax deleted successfully.", {}, status.HTTP_204_NO_CONTENT)
