from django.conf import settings
from django.db import models
from project.models import Project


# Create your models here.
class Task(models.Model):
    class TaskStatus(models.TextChoices):
        TODO = "TODO", "انجام نشده"
        IN_PROGRESS = "IN_PROGRESS", "درحال انجام"
        DONE = "DONE", "پایان"

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    project = models.ForeignKey(Project,
                                on_delete=models.CASCADE,
                                related_name='tasks')
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.PROTECT,
                                    related_name='assigned_tasks')

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='created_tasks')

    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   blank=True,
                                   null=True,
                                   on_delete=models.SET_NULL,
                                    related_name='updated_tasks')

    status = models.CharField(max_length=15,
                              choices=TaskStatus.choices,
                              default=TaskStatus.TODO)

    started_date = models.DateTimeField()
    deadline = models.DateTimeField()
    finished_date = models.DateTimeField(blank=True,
                                         null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title