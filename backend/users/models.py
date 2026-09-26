from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.

class User(AbstractUser):
    username = None
    email = models.EmailField(
        unique=True
    )
    phone = models.CharField(
        max_length = 11,
        blank = True,
        null = True,
        unique = True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email