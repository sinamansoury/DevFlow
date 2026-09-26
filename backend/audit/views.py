from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import AuditLog
from .serializers import AuditLogSerializer
from workspace.models import Workspace
from project.models import Project
from task.models import Task


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workspace_ids = Workspace.objects.filter(
            owner=self.request.user
        ).values_list("id", flat=True)

        project_ids = Project.objects.filter(
            workspace_id__in=workspace_ids
        ).values_list("id", flat=True)

        task_ids = Task.objects.filter(
            project_id__in=project_ids
        ).values_list("id", flat=True)

        return AuditLog.objects.filter(
            Q(
                entity_type="WORKSPACE",
                entity_id__in=workspace_ids,
            )
            |
            Q(
                entity_type="PROJECT",
                entity_id__in=project_ids,
            )
            |
            Q(
                entity_type="TASK",
                entity_id__in=task_ids,
            )
        ).order_by("-created_at")


