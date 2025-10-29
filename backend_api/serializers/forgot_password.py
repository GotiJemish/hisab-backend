# from django.core.mail import send_mail
# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from backend_api.models import EmailOTP
#
# User = get_user_model()
#
# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#
#     def validate(self, data):
#         email = data.get('email')
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("No account found with this email.")
#         data['user'] = user
#         return data
#
#     def create(self, validated_data):
#         user = validated_data['user']
#         otp_obj = EmailOTP.objects.create(user=user, purpose='forgot')
#         otp_code = otp_obj.generate_otp()
#         send_mail(
#             'Your Password Reset OTP',
#             f'Your OTP is: {otp_code}',
#             'noreply@example.com',
#             [user.email],
#             fail_silently=False,
#         )
#         return user
#
#
# class VerifyForgotOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)
#
#     def validate(self, data):
#         email = data['email']
#         otp = data['otp']
#         try:
#             user = User.objects.get(email=email)
#             otp_obj = EmailOTP.objects.filter(user=user, otp=otp, purpose='forgot', is_verified=False).last()
#             if not otp_obj:
#                 raise serializers.ValidationError("Invalid or expired OTP.")
#             otp_obj.is_verified = True
#             otp_obj.save()
#             data['user'] = user
#             return data
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User does not exist.")
#
# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     new_password = serializers.CharField(write_only=True, min_length=6)
#
#     def validate(self, data):
#         email = data['email']
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("User not found.")
#         otp_obj = EmailOTP.objects.filter(user=user, purpose='forgot', is_verified=True).last()
#         if not otp_obj:
#             raise serializers.ValidationError("OTP not verified.")
#         data['user'] = user
#         return data
#
#     def save(self):
#         user = self.validated_data['user']
#         new_password = self.validated_data['new_password']
#         user.set_password(new_password)
#         user.save()
#         return user


from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend_api.models import EmailOTP

User = get_user_model()

# ✅ Helper Mixin for standardized responses
class StandardResponseMixin:
    def get_success_response(self, message, data=None):
        return {
            "status": "success",
            "message": message,
            "data": data or {}
        }

    def get_error_response(self, message, errors=None):
        return {
            "status": "error",
            "message": message,
            "errors": errors or {}
        }


# 1️⃣ Forgot Password Serializer
class ForgotPasswordSerializer(StandardResponseMixin, serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(self.get_error_response(
                message="No account found with this email.",
                errors={"email": ["Email not registered."]}
            ))
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        otp_obj = EmailOTP.objects.create(user=user, purpose='forgot')
        otp_code = otp_obj.generate_otp()

        send_mail(
            subject='Your Password Reset OTP',
            message=f'Your OTP is: {otp_code}',
            from_email='noreply@example.com',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return self.get_success_response(
            message="OTP sent successfully to your email.",
            data={"email": user.email}
        )


# 2️⃣ Verify Forgot OTP Serializer
class VerifyForgotOTPSerializer(StandardResponseMixin, serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(self.get_error_response(
                message="User does not exist.",
                errors={"email": ["No user found with this email."]}
            ))

        otp_obj = EmailOTP.objects.filter(
            user=user, otp=otp, purpose='forgot', is_verified=False
        ).last()

        if not otp_obj:
            raise serializers.ValidationError(self.get_error_response(
                message="Invalid or expired OTP.",
                errors={"otp": ["OTP is invalid or expired."]}
            ))

        otp_obj.is_verified = True
        otp_obj.save()
        data['user'] = user
        return data

    def create(self, validated_data):
        return self.get_success_response(
            message="OTP verified successfully.",
            data={"email": validated_data['email']}
        )


# 3️⃣ Reset Password Serializer
class ResetPasswordSerializer(StandardResponseMixin, serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(self.get_error_response(
                message="User not found.",
                errors={"email": ["Invalid email."]}
            ))

        otp_obj = EmailOTP.objects.filter(
            user=user, purpose='forgot', is_verified=True
        ).last()

        if not otp_obj:
            raise serializers.ValidationError(self.get_error_response(
                message="OTP not verified.",
                errors={"otp": ["OTP verification is required before resetting password."]}
            ))

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return self.get_success_response(
            message="Password reset successfully.",
            data={"email": user.email}
        )
