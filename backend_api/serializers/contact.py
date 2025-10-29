
from rest_framework import serializers
from backend_api.models import Contact




class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'mobile', 'email', 'created_at','updated_at']
        read_only_fields = ['id', 'created_at']


