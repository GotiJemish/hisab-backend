# backend_api/serializers/account.py
from rest_framework import serializers
from backend_api.models import Account

class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at", "updated_at", "balance")
        extra_kwargs = {
            "name": {
                "error_messages": {
                    "blank": "Account name cannot be empty.",
                    "required": "Account name cannot be empty.",
                }
            }
        }

    def validate_name(self, value):
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Account name cannot be empty.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        name = attrs.get("name")
        if name:
            qs = Account.objects.filter(user=user, name__iexact=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"name": "An account with this name already exists."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)
