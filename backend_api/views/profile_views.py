# backend_api/views/profile_views.py
import os
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from backend_api.serializers.user import UserSerializer, CompanySerializer
from backend_api.utils.response_utils import success_response, error_response

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return success_response("Profile retrieved successfully.", serializer.data)

    def patch(self, request):
        user = request.user
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if first_name is not None:
            first_name = first_name.strip()
            if not first_name:
                return error_response("First name cannot be empty.", status.HTTP_400_BAD_REQUEST)
            user.first_name = first_name

        if last_name is not None:
            user.last_name = last_name.strip()

        user.save()
        serializer = UserSerializer(user)
        return success_response("Profile updated successfully.", serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return error_response("Both old and new passwords are required.", status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return error_response("Incorrect current password.", status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
            return error_response("Password must be at least 6 characters long.", status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return success_response("Password changed successfully.")


class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.company:
            return error_response("You do not belong to any company.", status.HTTP_400_BAD_REQUEST)
        
        serializer = CompanySerializer(user.company)
        return success_response("Company retrieved successfully.", serializer.data)

    def patch(self, request):
        user = request.user
        if not user.company:
            return error_response("You do not belong to any company.", status.HTTP_400_BAD_REQUEST)

        # Only allow Company Admin or System Super Admin to edit company details
        if user.role not in ["COMPANY_ADMIN", "SUPER_ADMIN"]:
            return error_response("You do not have permission to update company details.", status.HTTP_403_FORBIDDEN)

        company = user.company
        name = request.data.get("name")
        address = request.data.get("address")
        phone = request.data.get("phone")
        email = request.data.get("email")
        website = request.data.get("website")
        gstin = request.data.get("gstin")
        pan = request.data.get("pan")

        if name is not None:
            name = name.strip()
            if not name:
                return error_response("Company name cannot be empty.", status.HTTP_400_BAD_REQUEST)
            company.name = name

        if address is not None:
            company.address = address.strip()

        if phone is not None:
            company.phone = phone.strip()

        if email is not None:
            company.email = email.strip()

        if website is not None:
            company.website = website.strip()

        if gstin is not None:
            gstin = gstin.strip().upper()
            if not gstin:
                return error_response("GSTIN is required to complete company profile.", status.HTTP_400_BAD_REQUEST)
            if len(gstin) != 15:
                return error_response("GSTIN must be exactly 15 characters long.", status.HTTP_400_BAD_REQUEST)
            company.gstin = gstin

        if pan is not None:
            pan = pan.strip().upper()
            if not pan:
                return error_response("PAN is required to complete company profile.", status.HTTP_400_BAD_REQUEST)
            if len(pan) != 10:
                return error_response("PAN must be exactly 10 characters long.", status.HTTP_400_BAD_REQUEST)
            company.pan = pan

        company.save()
        serializer = CompanySerializer(company)
        return success_response("Company updated successfully.", serializer.data)


class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        image_file = request.FILES.get("profile_image")
        
        if not image_file:
            return error_response("No image file provided.", status.HTTP_400_BAD_REQUEST)
        
        # Validate format
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in allowed_extensions:
            return error_response(
                "Unsupported file format. Allowed formats: JPG, JPEG, PNG, WEBP.",
                status.HTTP_400_BAD_REQUEST
            )
        
        # Validate size (5MB max)
        max_size = 5 * 1024 * 1024
        if image_file.size > max_size:
            return error_response("File size exceeds the 5MB limit.", status.HTTP_400_BAD_REQUEST)
        
        # Remove old profile image file if exists
        if user.profile_image:
            try:
                user.profile_image.delete(save=False)
            except Exception:
                pass
            
        user.profile_image = image_file
        user.save()
        
        serializer = UserSerializer(user, context={"request": request})
        return success_response("Profile image updated successfully.", serializer.data)

    def delete(self, request):
        user = request.user
        if user.profile_image:
            try:
                user.profile_image.delete(save=False)
            except Exception:
                pass
            user.profile_image = None
            user.save()
            
        serializer = UserSerializer(user, context={"request": request})
        return success_response("Profile image removed successfully.", serializer.data)
