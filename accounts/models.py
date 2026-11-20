from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        GENERAL_USER = 'GENERAL_USER', 'General User'
        ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'
        ITEM_FINDER = 'ITEM_FINDER', 'Item Finder'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.GENERAL_USER,
        help_text="Role determining user permissions across the platform."
    )
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self):
        return self.role == self.Role.ADMINISTRATOR or self.is_superuser

    def is_finder(self):
        return self.role == self.Role.ITEM_FINDER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
