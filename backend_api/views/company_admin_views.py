from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from backend_api.models import Company
from backend_api.serializers.user import CompanySerializer
from backend_api.utils.response_utils import success_response, error_response

class AdminCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "SUPER_ADMIN":
            return Company.objects.all().order_by('-created_at')
        return Company.objects.none()

    def list(self, request, *args, **kwargs):
        if request.user.role != "SUPER_ADMIN":
            return error_response("You don't have permission to manage companies.", status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response("Companies retrieved successfully.", serializer.data)

    def update(self, request, *args, **kwargs):
        if request.user.role != "SUPER_ADMIN":
            return error_response("You don't have permission to update companies.", status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response("Company updated successfully.", serializer.data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)
