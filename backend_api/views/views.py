from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from backend_api.serializers import ResendOTPSerializer, ContactSerializer, OTPVerifySerializer, LoginSerializer, InvoiceSerializer,CustomTokenObtainPairSerializer, ForgotPasswordSerializer, VerifyForgotOTPSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView



class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Email verified successfully. Account created."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if user is verified
        if not user.is_active:
            return Response({"detail": "Email not verified. Access denied."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateInvoiceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InvoiceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            invoice = serializer.save()
            return Response({
                "message": "Invoice created successfully",
                "bill_id": invoice.bill_id
            }, status=status.HTTP_201_CREATED)
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


