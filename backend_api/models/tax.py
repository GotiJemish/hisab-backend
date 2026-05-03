import uuid
from django.db import models

class Tax(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('backend_api.Company', on_delete=models.CASCADE, related_name='taxes')
    name = models.CharField(max_length=50) # e.g., GST 18%, VAT 5%
    rate = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 18.00
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('company', 'name')

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
