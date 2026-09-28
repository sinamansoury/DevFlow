from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import AuditLog
from .serializers import AuditLogSerializer
from workspace.models import Workspace
from project.models import Project
from task.models import Task


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    search_fields = [
        "entity_name",
    ]

    ordering_fields = [
        "created_at",
        "entity_type",
        "action",
    ]

    @extend_schema(
        summary="لیست Audit Log ها",
        description="نمایش تاریخچه عملیات انجام‌شده در Workspace، Project و Task های تحت مالکیت کاربر.",
        tags=["Audit Log"],
        parameters=[
            OpenApiParameter(
                name="entity_type",
                description="فیلتر بر اساس نوع موجودیت",
                required=False,
                type=str,
                enum=["WORKSPACE", "PROJECT", "TASK"],
            ),
            OpenApiParameter(
                name="action",
                description="فیلتر بر اساس نوع عملیات",
                required=False,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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

        queryset = AuditLog.objects.filter(
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
        )

        entity_type = self.request.query_params.get("entity_type")
        action = self.request.query_params.get("action")

        if entity_type:
            queryset = queryset.filter(entity_type=entity_type)

        if action:
            queryset = queryset.filter(action=action)

        return queryset.order_by("-created_at")