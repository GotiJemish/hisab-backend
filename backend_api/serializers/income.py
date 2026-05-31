# backend_api/serializers/income.py
from rest_framework import serializers
from backend_api.models import Income, Account

class IncomeSerializer(serializers.ModelSerializer):
    account_name = serializers.ReadOnlyField(source="account.name")

    class Meta:
        model = Income
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_account(self, value):
        user = self.context["request"].user
        if value.user != user:
            raise serializers.ValidationError("Invalid account selected.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
