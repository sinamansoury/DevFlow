from django.db import models

from django.conf import settings


# Create your models here.

class Workspace(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_workspaces',
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='workspaces',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
