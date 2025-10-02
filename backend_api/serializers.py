from django.core.cache import cache
from rest_framework import serializers
from .models import User, EmailOTP,Contact,Invoice, InvoiceItem
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password



class RegisterSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password','user_id']
        extra_kwargs = {'password': {'write_only': True}}


    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        # Generate OTP
        import random
        otp_code = str(random.randint(100000, 999999))

        # Save data in cache instead of creating user
        cache.set(f'registration_{email}', {
            'email': email,
            'password': password,
            'otp': otp_code
        }, timeout=600)

        # Send OTP
        self.send_otp_email(email, otp_code)

        return validated_data

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
        cached_data = cache.get(f'registration_{email}')
        try:
            if not cached_data:
                raise serializers.ValidationError("OTP expired or invalid request.")

            if cached_data['otp'] != otp_input:
                raise serializers.ValidationError("Invalid OTP.")


            user = User.objects.create_user(
                email=cached_data['email'],
                password=cached_data['password'],
                is_active=True  # Active since verified
            )

            # Clean up cache
            cache.delete(f'registration_{email}')

            data['user'] = user
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError(_("Both email and password are required."))

        # Authenticate using email as the username field
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError(_("Invalid credentials or user not verified."))

        if not user.is_active:
            raise serializers.ValidationError(_("Account is inactive. Please verify your email."))

        # Attach user to validated data
        data['user'] = user
        return data


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'mobile', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']



class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'rate', 'discount']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['contact', 'supply_type', 'invoice_date', 'items']

    def validate_contact(self, contact):
        user = self.context['request'].user
        if contact.user != user:
            raise serializers.ValidationError("You can only create invoices for your own contacts.")
        return contact

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user

        invoice = Invoice.objects.create(user=user, **validated_data)

        total_amount = 0
        for item_data in items_data:
            quantity = item_data['quantity']
            rate = item_data['rate']
            discount = item_data.get('discount', 0)

            total = (quantity * rate) - discount
            total_amount += total

            InvoiceItem.objects.create(
                invoice=invoice,
                total=total,
                **item_data
            )

        invoice.total_amount = total_amount
        invoice.save()

        return invoice
