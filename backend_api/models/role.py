import uuid
from django.db import models

class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('backend_api.Company', on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=50)
    permissions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('company', 'name')

    def __str__(self):
        return f"{self.name} - {self.company.name if self.company else 'System'}"
