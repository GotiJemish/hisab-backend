from rest_framework import serializers
from backend_api.models.role import Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['company'] = user.company
        return super().create(validated_data)
