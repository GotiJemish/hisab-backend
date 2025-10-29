# # backend_api/serializers/auth.py
# from django.contrib.auth import authenticate
# from django.utils.translation import gettext_lazy as _
# from rest_framework import serializers
# from django.core.cache import cache
# from django.core.mail import send_mail
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from backend_api.models import User
# import random, time
#
#
# # 1️⃣ Register Serializer
# class RegisterSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#
#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Email already registered.")
#         return value
#
#     def create(self, validated_data):
#         email = validated_data['email']
#         otp_code = str(random.randint(100000, 999999))
#
#         cache.set(f'registration_{email}', {'email': email, 'otp': otp_code}, timeout=600)
#
#         send_mail(
#             'Your Registration OTP Code',
#             f'Your OTP is: {otp_code}',
#             'noreply@example.com',
#             [email],
#             fail_silently=False,
#         )
#         return validated_data
#
#
# # 2️⃣ OTP Verify Serializer
# class OTPVerifySerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)
#     password = serializers.CharField(write_only=True, min_length=6)
#
#     def validate(self, data):
#         email = data.get("email")
#         otp_input = data.get("otp")
#
#         cached_data = cache.get(f'registration_{email}')
#         if not cached_data:
#             raise serializers.ValidationError("OTP expired or invalid request.")
#         if cached_data['otp'] != otp_input:
#             raise serializers.ValidationError("Invalid OTP.")
#         if User.objects.filter(email=email).exists():
#             raise serializers.ValidationError("Email already verified and registered.")
#         return data
#
#     def create(self, validated_data):
#         email = validated_data['email']
#         password = validated_data['password']
#         user = User.objects.create_user(email=email, password=password, is_active=True)
#         cache.delete(f'registration_{email}')
#         return user
#
#
# # 3️⃣ Login Serializer
# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)
#
#     def validate(self, data):
#         user = authenticate(username=data.get('email'), password=data.get('password'))
#         if not user:
#             raise serializers.ValidationError(_("Invalid credentials or user not verified."))
#         if not user.is_active:
#             raise serializers.ValidationError(_("Account is inactive. Please verify your email."))
#         data['user'] = user
#         return data
#
#
# # 4️⃣ Custom Token Serializer
# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['user_id'] = str(user.id)
#         token['email'] = user.email
#         return token
#
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         data.update({
#             'user_id': str(self.user.id),
#             'email': self.user.email,
#         })
#         return data
#
#
# # 5️⃣ Resend OTP Serializer
# class ResendOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     purpose = serializers.ChoiceField(choices=["register", "forgot"])
#
#     def validate(self, data):
#         email, purpose = data["email"], data["purpose"]
#
#         otp_key = f"otp_{purpose}_{email}"
#         cooldown_key = f"cooldown_{purpose}_{email}"
#
#         last_sent = cache.get(cooldown_key)
#         now = time.time()
#         if last_sent and now - last_sent < 60:
#             raise serializers.ValidationError("Please wait 60 seconds before requesting a new OTP.")
#
#         if purpose == "register" and User.objects.filter(email=email).exists():
#             raise serializers.ValidationError("Email already registered.")
#         elif purpose == "forgot" and not User.objects.filter(email=email, is_active=True).exists():
#             raise serializers.ValidationError("No active account with this email.")
#
#         otp_data = cache.get(otp_key)
#         otp_code = otp_data["otp"] if otp_data else str(random.randint(100000, 999999))
#         cache.set(otp_key, {"otp": otp_code}, timeout=600)
#
#         send_mail(
#             subject="Your OTP Code",
#             message=f"Your OTP for {purpose} is: {otp_code}",
#             from_email="noreply@example.com",
#             recipient_list=[email],
#             fail_silently=False,
#         )
#
#         cache.set(cooldown_key, now, timeout=60)
#         return data



from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from backend_api.models import User
import random, time


# 1️⃣ REGISTER SERIALIZER
class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "success": False,
                "message": "This email is already registered."
            })
        return value

    def create(self, validated_data):
        email = validated_data.get('email')

        # Generate OTP
        otp_code = str(random.randint(100000, 999999))

        # Store OTP in cache (10 minutes)
        cache_key = f'registration_{email}'
        cache.set(cache_key, {'email': email, 'otp': otp_code}, timeout=600)

        try:
            # Send OTP email
            send_mail(
                subject='Your Registration OTP Code',
                message=f'Your OTP for registration is: {otp_code}',
                from_email='noreply@example.com',
                recipient_list=[email],
                fail_silently=False,
            )

            response_data = {
                "success": True,
                "message": "OTP sent successfully to your email address.",
                "data": {
                    "email": email,
                    "otp_valid_for": "10 minutes",
                    "resend_available_in": "60 seconds"
                }
            }

        except Exception as e:
            response_data = {
                "success": False,
                "message": "Failed to send OTP. Please try again later.",
                "error": str(e)
            }

        return response_data


# 2️⃣ OTP VERIFY SERIALIZER
class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        email = data.get("email")
        otp_input = data.get("otp")

        cached_data = cache.get(f'registration_{email}')
        if not cached_data:
            raise serializers.ValidationError({
                "success": False,
                "message": "OTP expired or invalid request. Please register again."
            })
        if cached_data['otp'] != otp_input:
            raise serializers.ValidationError({
                "success": False,
                "message": "Invalid OTP entered. Please check and try again."
            })
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "success": False,
                "message": "Email already verified and registered."
            })
        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(email=email, password=password, is_active=True)
        cache.delete(f'registration_{email}')
        return {
            "success": True,
            "message": "Email verified successfully. Account created.",
            "data": {"email": user.email, "user_id": str(user.id)}
        }


# 3️⃣ LOGIN SERIALIZER
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check if both fields provided
        if not email or not password:
            raise serializers.ValidationError({
                "success": False,
                "message": "Both email and password are required."
            })

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "success": False,
                "message": "No account found with this email."
            })

        # Verify password manually before authenticate()
        if not user.check_password(password):
            raise serializers.ValidationError({
                "success": False,
                "message": "Incorrect password. Please try again."
            })

        # Verify account status
        if not user.is_active:
            raise serializers.ValidationError({
                "success": False,
                "message": "Account inactive. Please verify your email before logging in."
            })

        # Authenticate (optional double check, handles custom backends)
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({
                "success": False,
                "message": "Invalid credentials or authentication failure."
            })

        # ✅ Success
        data['user'] = user
        data['response'] = {
            "success": True,
            "message": "Login successful.",
            "data": {
                "user_id": str(user.id),
                "email": user.email,
                "full_name": getattr(user, "full_name", ""),
                "is_active": user.is_active,
            }
        }
        return data



# 4️⃣ CUSTOM TOKEN SERIALIZER
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.id)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            "success": True,
            "message": "Token generated successfully.",
            "data": {
                "access": data["access"],
                "refresh": data["refresh"],
                "user_id": str(self.user.id),
                "email": self.user.email
            }
        })
        return data


# 5️⃣ RESEND OTP SERIALIZER
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=["register", "forgot"])

    def validate(self, data):
        email, purpose = data["email"], data["purpose"]

        otp_key = f"otp_{purpose}_{email}"
        cooldown_key = f"cooldown_{purpose}_{email}"

        last_sent = cache.get(cooldown_key)
        now = time.time()
        if last_sent and now - last_sent < 60:
            raise serializers.ValidationError({
                "success": False,
                "message": "Please wait 60 seconds before requesting a new OTP."
            })

        if purpose == "register" and User.objects.filter(email=email).exists():
            raise serializers.ValidationError({
                "success": False,
                "message": "Email already registered. Please login instead."
            })
        elif purpose == "forgot" and not User.objects.filter(email=email, is_active=True).exists():
            raise serializers.ValidationError({
                "success": False,
                "message": "No active account found for this email."
            })

        otp_data = cache.get(otp_key)
        otp_code = otp_data["otp"] if otp_data else str(random.randint(100000, 999999))
        cache.set(otp_key, {"otp": otp_code}, timeout=600)

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP for {purpose} is: {otp_code}",
            from_email="noreply@example.com",
            recipient_list=[email],
            fail_silently=False,
        )

        cache.set(cooldown_key, now, timeout=60)

        return {
            "success": True,
            "message": f"OTP sent successfully for {purpose}.",
            "data": {"email": email, "otp_valid_for": "10 minutes"}
        }
