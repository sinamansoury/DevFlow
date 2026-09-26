from django.conf import settings
from django.db import models



# Create your models here.
class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "ایجاد"
        UPDATE = "UPDATE", "ویرایش"
        DELETE = "DELETE", "حذف"
        ADD_MEMBER = "ADD_MEMBER", "افزودن عضو"
        REMOVE_MEMBER = "REMOVE_MEMBER", "حذف عضو"
        UPDATE_STATUS = "UPDATE_STATUS", "تغییر وضعیت"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )

    entity_type = models.CharField(max_length=20)
    entity_id = models.IntegerField()
    entity_name = models.CharField(max_length=150)

    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )

    old_value = models.JSONField(
        blank=True,
        null=True
    )

    new_value = models.JSONField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)