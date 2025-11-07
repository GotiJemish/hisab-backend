# backend_api/views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from backend_api.serializers import RegisterSerializer, VerifyRegisterOTPSerializer, SetPasswordSerializer, \
    CustomTokenObtainPairSerializer, LoginSerializer, ResendOTPSerializer, ForgotPasswordSerializer, \
    VerifyForgotOTPSerializer, ResetPasswordSerializer
from backend_api.utils.response_utils import success_response, error_response


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("OTP sent to your email.")
        return error_response("Invalid registration details.", status.HTTP_400_BAD_REQUEST)


class VerifyRegisterOTPView(APIView):
    def post(self, request):
        serializer = VerifyRegisterOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(
                "Email verified successfully.",
                data=serializer.validated_data.get("data")
            )
        return error_response(serializer.errors.get("non_field_errors", ["Invalid OTP."])[0])

class SetPasswordView(APIView):
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return success_response("Password set successfully.")
        return error_response("Failed to set password.")


# 9️⃣ CUSTOM TOKEN (JWT)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            refresh['user_id'] = str(user.id)
            refresh['email'] = user.email
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": str(user.id)
            }
            return success_response("Login successful.", data=data)
        return error_response("Invalid credentials or unverified user.")

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success_response("OTP resent to your email.")
        return error_response("Failed to resend OTP.")

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("OTP sent to your email for password reset.")
        return error_response("No account found with this email.")

class VerifyForgotOTPView(APIView):
    def post(self, request):
        serializer = VerifyForgotOTPSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(
                "OTP verified successfully. You can now reset your password.",
                data=serializer.validated_data
            )
        return error_response("Invalid or expired OTP.")

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response("Password has been reset successfully.")
        return error_response("Password reset failed. Invalid data.")



