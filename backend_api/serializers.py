from rest_framework import serializers
from .models import User, EmailOTP
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    class Meta:
        model = User
        fields = ['email', 'password','user_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        otp = EmailOTP.objects.create(user=user)
        otp_code = otp.generate_otp()
        # Send email here
        self.send_otp_email(user.email, otp_code)
        return user

    def send_otp_email(self, email, otp):
        from django.core.mail import send_mail
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp}',
            'noreply@example.com',
            [email],
            fail_silently=False,
        )



class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get("email")
        otp_input = data.get("otp")

        try:
            user = User.objects.get(email=email)
            otp_obj = EmailOTP.objects.filter(user=user, otp=otp_input, is_verified=False).last()
            if not otp_obj:
                raise serializers.ValidationError("Invalid OTP or already used.")
            otp_obj.is_verified = True
            otp_obj.save()
            user.is_active = True
            user.save()
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)  # username=email is important here
        if not user:
            raise serializers.ValidationError("Invalid credentials or user not verified.")
        if not user.is_active:
            raise serializers.ValidationError("Account not active. Verify your email.")
        data['user'] = user
        return data
