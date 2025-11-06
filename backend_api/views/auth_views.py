# backend_api/views/auth_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from backend_api.serializers import RegisterSerializer, VerifyRegisterOTPSerializer, SetPasswordSerializer, \
    CustomTokenObtainPairSerializer, LoginSerializer, ResendOTPSerializer, ForgotPasswordSerializer, \
    VerifyForgotOTPSerializer, ResetPasswordSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OTP sent to your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyRegisterOTPView(APIView):
    def post(self, request):
        serializer = VerifyRegisterOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Email verified successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(APIView):
    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": str(user.id)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "OTP sent successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OTP sent to your email for password reset."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyForgotOTPView(APIView):
    def post(self, request):
        serializer = VerifyForgotOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"detail": "OTP verified successfully. You can now reset your password."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password reset successful. You can now log in."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



