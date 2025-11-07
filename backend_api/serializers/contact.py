# backend_api/serializers/contact.py
from rest_framework import serializers
from backend_api.models import Contact
import re


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def validate_mobile(self, value):
        if not re.match(r'^\+?\d+$', value):
            raise serializers.ValidationError("Mobile number must contain only digits or start with '+'.")
        return value

    def validate_pan(self, value):
        """PAN format: 5 letters + 4 digits + 1 letter (e.g., ABCDE1234F)"""
        if value and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', value):
            raise serializers.ValidationError(
                "Invalid PAN format. It should be 5 letters, 4 digits, and 1 letter (e.g., ABCDE1234F)."
            )
        return value

    def validate_gst(self, value):
        """GST format: 15 characters (alphanumeric)"""
        if value and not re.match(r'^[0-9A-Z]{15}$', value):
            raise serializers.ValidationError("Invalid GST format. It should be 15 alphanumeric characters.")
        return value
    # def create(self, validated_data):
    #     # Automatically assign logged-in user
    #     user = self.context['request'].user
    #     validated_data['user'] = user
    #     return super().create(validated_data)
