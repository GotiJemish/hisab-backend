# backend_api/serializers/forgot_password.py
from rest_framework import serializers
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from backend_api.models import User, EmailOTP
import random


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError({"success": False, "message": "No active user with this email."})
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        email = user.email

        EmailOTP.objects.filter(user=user, purpose='forgot').delete()
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.create(user=user, otp=otp, purpose='forgot')

        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP to reset password is: {otp}",
            from_email="noreply@example.com",
            recipient_list=[email],
            fail_silently=False,
        )

        return {"success": True, "message": "OTP sent successfully."}


class VerifyForgotOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email, otp = data['email'], data['otp']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"success": False, "message": "User not found."})

        otp_entry = EmailOTP.objects.filter(
            user=user,
            otp=otp,
            purpose='forgot',
            is_verified=False,
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).last()

        if not otp_entry:
            raise serializers.ValidationError({"success": False, "message": "Invalid or expired OTP."})

        otp_entry.is_verified = True
        otp_entry.save()
        return {
            "email": user.email,
            "user_id": str(user.id)
        }

    def create(self, validated_data):
        return {"success": True, "message": "OTP verified successfully."}


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"success": False, "message": "User not found."})

        otp_verified = EmailOTP.objects.filter(
            user=user,
            purpose='forgot',
            is_verified=True,
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).exists()

        if not otp_verified:
            raise serializers.ValidationError({"success": False, "message": "OTP not verified or expired."})
        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['new_password'])
        user.save()
        EmailOTP.objects.filter(user=user, purpose='forgot').delete()

        return {"success": True, "message": "Password reset successfully."}
