# backend_api/models/email_otp.py
from django.db import models
from .user import User
import random


class EmailOTP(models.Model):
    PURPOSE_CHOICES = [
        ('register', 'Register'),
        ('forgot', 'Forgot Password'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='register')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.otp}'

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.save()
        return self.otp
