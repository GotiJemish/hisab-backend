# backend_api/serializers/auth.py
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from backend_api.models import User, EmailOTP
import random
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



# ✅ 1️⃣ REGISTER SERIALIZER
class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=True)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user and user.is_verified:
            # Note: We are allowing multiple users, but for top-level org registration, we might just warn
            # However we should allow it if multi-tenancy uniqueness is removed.
            pass
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        company_name = validated_data.get("company_name", "").strip()

        EmailOTP.objects.filter(user__email=email, purpose="register").delete()

        company = None
        if company_name:
            from backend_api.models.company import Company
            company = Company.objects.create(name=company_name)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
                "is_active": False,
                "company": company,
                "role": "COMPANY_ADMIN" if company_name else "STAFF"
            },
        )

        if not created and not user.is_active:
            user.first_name = validated_data["first_name"]
            user.last_name = validated_data["last_name"]
            if company:
                user.company = company
                user.role = "COMPANY_ADMIN"
            user.save()

        # Generate new OTP
        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.create(user=user, otp=otp, purpose="register")

        # Send OTP via email
        send_mail(
            subject="Your Registration OTP Code",
            message=f"Your OTP for registration is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return {
            "success": True,
            "message": "OTP sent successfully to your email address.",
            "data": {"email": email, "otp_valid_for": "10 minutes"},
        }


# 1️⃣ REGISTER SERIALIZER
class VerifyRegisterOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email, otp = data["email"], data["otp"]

        user = User.objects.filter(email=email).order_by('-date_joined').first()
        if not user:
            raise serializers.ValidationError(
                {"success": False, "message": "User not found."}
            )

        # valid_from = timezone.now() - timedelta(minutes=10)
        otp_entry = EmailOTP.objects.filter(
            user=user,
            otp=otp,
            purpose="register",
            is_verified=False,
            created_at__gte=timezone.now() - timedelta(minutes=10),
        ).last()
        if not otp_entry:
            raise serializers.ValidationError(
                {"success": False, "message": "Invalid or expired OTP."}
            )
        # OTP expired (>10 minutes old)
        # if otp_entry.created_at < timezone.now() - timedelta(minutes=10):
        #     raise serializers.ValidationError({
        #         "success": False,
        #         "message": "OTP expired. Please register again."
        #     })

        # ✅ Mark verified
        otp_entry.is_verified = True
        otp_entry.save()

        # ✅ Mark user verified
        user.is_verified = True
        user.is_active = True
        user.save()

        # ✅ Delete all OTPs for this user/purpose
        EmailOTP.objects.filter(user=user, purpose="register").delete()

        return {
            "success": True,
            "message": "Email verified successfully.",
            "data": {
                "email": user.email,
                "user_id": str(user.id),
            },
        }

    def create(self, validated_data):
        return validated_data


# 3️⃣ SET PASSWORD AFTER VERIFICATION
class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        user = User.objects.filter(email=data["email"]).order_by('-date_joined').first()
        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.is_verified:
            raise serializers.ValidationError(
                "Email not verified yet. Please verify your account first."
            )

        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        user.set_password(validated_data["password"])
        user.save()
        return {"success": True, "message": "Password set successfully."}


# 4️⃣ LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email, password = data["email"], data["password"]
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError(
                {"success": False, "message": "Invalid credentials."}
            )

        if not user.is_verified:
            raise serializers.ValidationError(
                {
                    "success": False,
                    "message": "Account not verified. Please verify your email first.",
                }
            )

        # ✅ Return user so the view can access it
        data["user"] = user
        return data


# 5️⃣ RESEND OTP SERIALIZER
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=["register", "forgot"])

    def validate(self, data):
        email, purpose = data["email"], data["purpose"]

        if (
            purpose == "register"
            and User.objects.filter(email=email, is_active=True).exists()
        ):
            raise serializers.ValidationError(
                {"success": False, "message": "Email already verified. Please login."}
            )

        if (
            purpose == "forgot"
            and not User.objects.filter(email=email, is_active=True).exists()
        ):
            raise serializers.ValidationError(
                {"success": False, "message": "No active user found for this email."}
            )

        return data

    def create(self, validated_data):
        email, purpose = validated_data["email"], validated_data["purpose"]
        user = User.objects.filter(email=email).order_by('-date_joined').first()
        if not user:
            raise serializers.ValidationError("User not found.")

        # Delete old OTPs
        EmailOTP.objects.filter(user=user, purpose=purpose).delete()

        otp = str(random.randint(100000, 999999))
        EmailOTP.objects.create(user=user, otp=otp, purpose=purpose)

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP for {purpose} is: {otp}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return {"success": True, "message": f"OTP sent successfully for {purpose}."}


# 4️⃣ Custom Token Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["user_id"] = str(user.id)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "user_id": str(self.user.id),
                "email": self.user.email,
            }
        )
        return data
