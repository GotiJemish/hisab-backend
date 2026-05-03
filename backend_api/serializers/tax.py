from rest_framework import serializers
from backend_api.models.tax import Tax

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id', 'name', 'rate', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['company'] = user.company
        return super().create(validated_data)
