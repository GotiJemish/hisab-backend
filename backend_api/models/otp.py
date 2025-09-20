from django.db import models
from .user import User

class EmailOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.email} - {self.otp}'

    def generate_otp(self):
        import random
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp
