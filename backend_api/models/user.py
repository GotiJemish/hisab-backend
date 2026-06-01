# backend_api/models/user.py
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Group,
    Permission,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField()
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'System Super Admin'),
        ('COMPANY_ADMIN', 'Company Admin'),
        ('STAFF', 'Staff User'),
    ]
    company = models.ForeignKey(
        'backend_api.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='COMPANY_ADMIN')
    
    custom_role = models.ForeignKey(
        'backend_api.Role', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_users'
    )

    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    # Store dynamic permissions like {"invoices": {"create": True, "read": True}}
    permissions = models.JSONField(default=dict, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        unique_together = ('email', 'company')

    def __str__(self):
        return self.email
