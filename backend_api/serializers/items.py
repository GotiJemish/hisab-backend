# backend_api/serializers/items.py

from rest_framework import serializers
from backend_api.models import Items
import re


class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Items
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")

    # -----------------------------
    # FIELD-LEVEL VALIDATIONS
    # -----------------------------

    def validate_name(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Item name cannot be empty.")
        return value

    def validate_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Rate cannot be negative.")
        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount cannot be negative.")
        return value

    # -----------------------------
    # OBJECT-LEVEL VALIDATION
    # -----------------------------
    def validate(self, attrs):
        rate = attrs.get("rate", 0)
        discount = attrs.get("discount", 0)

        if discount and discount > rate:
            raise serializers.ValidationError({
                "discount": "Discount cannot be greater than rate."
            })

        return attrs

    # -----------------------------
    # CREATE (Auto-assign user)
    # -----------------------------
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
