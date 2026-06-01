# backend_api/serializers/user.py
from rest_framework import serializers
from backend_api.models import User, Company

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'phone', 'email', 'gstin', 'pan', 'website', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True)
    custom_role_name = serializers.CharField(source='custom_role.name', read_only=True)
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role', 
            'custom_role', 'custom_role_name', 'permissions', 
            'is_active', 'company', 'profile_image', 'profile_image_url'
        ]

    def get_profile_image_url(self, obj):
        request = self.context.get('request')
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

class CreateUserSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    role = serializers.CharField(max_length=20, default='STAFF')
    custom_role_id = serializers.UUIDField(required=False, allow_null=True)
    permissions = serializers.JSONField(default=dict)
    
    def validate_email(self, value):
        user = self.context.get('request').user if self.context.get('request') else None
        
        # If user is being created for a specific company, we don't do global uniqueness
        # We rely on unique_together constraints
        return value
