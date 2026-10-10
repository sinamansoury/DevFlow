
from celery import shared_task

from .models import Notification


@shared_task
def create_task_assigned_notification(recipient_id,task_id,task_title,assigner_name,):
    message = (
        f"{assigner_name} تسک «{task_title}» را "
        "به شما اختصاص داد."
    )

    return Notification.objects.create(
        recipient_id=recipient_id,
        notification_type=Notification.NotificationType.TASK_ASSIGNED,
        title="تسک جدید به شما اختصاص داده شد",
        message=message,
        task_id=task_id,
    ).id