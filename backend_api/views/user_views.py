# backend_api/views/user_views.py
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from backend_api.models import User
from backend_api.serializers.user import UserSerializer, CreateUserSerializer
from backend_api.utils.response_utils import success_response, error_response
import random
from django.core.mail import send_mail

class UserViewSet(viewsets.ModelViewSet):
    """
    User Management API for Company Admins
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.company:
            # Users belonging to the same company
            return User.objects.filter(company=user.company).order_by("-date_joined")
        # If no company, they can only see themselves
        return User.objects.filter(id=user.id)

    def create(self, request, *args, **kwargs):
        admin = request.user
        
        # Auto-migrate legacy standalone admins to have a company if they lack one
        if not admin.company:
            from backend_api.models.company import Company
            company_name = f"{admin.first_name} {admin.last_name} Company".strip()
            if not company_name or company_name == "Company":
                company_name = f"{admin.email}'s Company"
            company = Company.objects.create(name=company_name)
            admin.company = company
            admin.role = 'COMPANY_ADMIN'
            admin.save()

        if not admin.company or admin.role not in ["COMPANY_ADMIN", "SUPER_ADMIN"]:
            return error_response("You don't have permission to add users.", status.HTTP_403_FORBIDDEN)
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            temp_password = str(random.randint(10000000, 99999999)) # temporary password
            
            new_user = User.objects.create(
                email=email,
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                role=serializer.validated_data["role"],
                permissions=serializer.validated_data["permissions"],
                company=admin.company,
                is_active=True,
                is_verified=True # Auto verify users added by admin
            )
            new_user.set_password(temp_password)
            new_user.save()

            # Email user their temporary password
            try:
                send_mail(
                    "You've been invited to Hisaab",
                    f"Hello {new_user.first_name},\n\nYou have been invited to join {admin.company.name} on Hisaab.\n\nYour login email: {email}\nYour temporary password: {temp_password}\n\nPlease log in and change your password.",
                    "noreply@example.com",
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                pass # Fail silently for email in dev

            return success_response(
                "User added successfully. An email with temporary password has been sent.",
                UserSerializer(new_user).data,
                status.HTTP_201_CREATED
            )
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        admin = request.user
        if not admin.company or admin.role not in ["COMPANY_ADMIN", "SUPER_ADMIN"]:
            return error_response("You don't have permission to update users.", status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            instance.first_name = serializer.validated_data["first_name"]
            instance.last_name = serializer.validated_data["last_name"]
            instance.role = serializer.validated_data["role"]
            instance.permissions = serializer.validated_data["permissions"]
            instance.save()
            return success_response("User updated successfully.", UserSerializer(instance).data)
        return error_response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        admin = request.user
        if not admin.company or admin.role not in ["COMPANY_ADMIN", "SUPER_ADMIN"]:
            return error_response("You don't have permission to delete users.", status.HTTP_403_FORBIDDEN)
            
        instance = self.get_object()
        if instance.id == admin.id:
            return error_response("You cannot delete yourself.", status.HTTP_400_BAD_REQUEST)
            
        instance.delete()
        return success_response("User deleted successfully.", {}, status.HTTP_204_NO_CONTENT)
