from django.db import models
from workspace.models import Workspace


# Create your models here.
class Project(models.Model):
    class Meta:
        ordering = ["-created_at"]
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='projects',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



