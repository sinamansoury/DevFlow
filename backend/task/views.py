from django.utils import timezone
from django.db.models import Q

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated



from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from audit.models import AuditLog
from .models import Task
from .permissions import (
    IsTaskWorkspaceMember,
    IsTaskWorkspaceOwner,
)
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]


    search_fields = [
        "title",
        "description",
    ]

    filterset_fields = [
        "status",
        "project",
        "assigned_to",
    ]

    ordering_fields = [
        "title",
        "started_date",
        "deadline",
        "created_at",
        "updated_at",
        "status",
    ]

    @extend_schema(
        summary="لیست Taskها",
        description=(
            "نمایش Taskهای Workspaceهایی که کاربر "
            "Owner یا Member آن‌هاست."
        ),
        tags=["Task"],
        parameters=[
            OpenApiParameter(
                name="status",
                description="فیلتر بر اساس وضعیت Task",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="project",
                description="فیلتر بر اساس Project ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="assigned_to",
                description="فیلتر بر اساس User ID",
                required=False,
                type=int,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ایجاد Task",
        description=(
            "ایجاد یک Task جدید. "
            "فقط Owner Workspace پروژه می‌تواند Task ایجاد کند."
        ),
        tags=["Task"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "project",
                "project__workspace",
                "assigned_to",
                "created_by",
                "updated_by",
            )
            .filter(
                Q(project__workspace__owner=self.request.user)
                | Q(project__workspace__members=self.request.user)
            )
            .distinct()
        )

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if project.workspace.owner != self.request.user:
            raise PermissionDenied()

        task = serializer.save(
            created_by=self.request.user
        )

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="TASK",
            entity_id=task.id,
            entity_name=task.title,
            action=AuditLog.Action.CREATE,
        )


class TaskRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = TaskSerializer
    lookup_url_kwarg = "id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            permission_classes = [
                IsAuthenticated,
                IsTaskWorkspaceOwner,
            ]
        else:
            permission_classes = [
                IsAuthenticated,
                IsTaskWorkspaceMember,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    @extend_schema(
        summary="دریافت Task",
        description=(
            "نمایش اطلاعات Task برای Owner یا Member "
            "Workspace."
        ),
        tags=["Task"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش Task",
        description=(
            "Owner می‌تواند اطلاعات Task را ویرایش کند. "
            "Member فقط می‌تواند status را تغییر دهد."
        ),
        tags=["Task"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش Task",
        description=(
            "Owner می‌تواند اطلاعات Task را ویرایش کند. "
            "Member فقط می‌تواند status را تغییر دهد."
        ),
        tags=["Task"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="حذف Task",
        description=(
            "حذف Task. فقط Owner Workspace مجاز است."
        ),
        tags=["Task"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Task.objects
            .select_related(
                "project",
                "project__workspace",
                "assigned_to",
                "created_by",
                "updated_by",
            )
            .filter(
                Q(project__workspace__members=self.request.user)
                | Q(project__workspace__owner=self.request.user)
            )
            .distinct()
        )

    def perform_update(self, serializer):
        task = serializer.instance
        workspace = task.project.workspace

        def make_json_safe(value):
            if hasattr(value, "isoformat"):
                return value.isoformat()

            if hasattr(value, "pk"):
                return value.pk

            return value

        serializer.validated_data.pop(
            "finished_date",
            None,
        )

        new_status = serializer.validated_data.get(
            "status",
            task.status,
        )

        extra_data = {}

        if new_status == "DONE" and task.status != "DONE":
            extra_data["finished_date"] = timezone.now()

        elif new_status != "DONE" and task.finished_date:
            extra_data["finished_date"] = None

        if workspace.owner == self.request.user:

            old_value = {
                field: make_json_safe(
                    getattr(task, field)
                )
                for field in serializer.validated_data.keys()
            }

            serializer.save(
                updated_by=self.request.user,
                **extra_data,
            )

            task.refresh_from_db()

            new_value = {
                field: make_json_safe(
                    getattr(task, field)
                )
                for field in serializer.validated_data.keys()
            }

            if "status" in serializer.validated_data:
                new_value["status"] = task.status

            if "finished_date" in extra_data:
                new_value["finished_date"] = make_json_safe(
                    task.finished_date
                )

            AuditLog.objects.create(
                user=self.request.user,
                entity_type="TASK",
                entity_id=task.id,
                entity_name=task.title,
                action=AuditLog.Action.UPDATE,
                old_value=old_value,
                new_value=new_value,
            )

            return

        if set(serializer.validated_data.keys()) != {"status"}:
            raise PermissionDenied()

        old_status = task.status

        serializer.save(
            updated_by=self.request.user,
            **extra_data,
        )

        task.refresh_from_db()

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="TASK",
            entity_id=task.id,
            entity_name=task.title,
            action=AuditLog.Action.UPDATE_STATUS,
            old_value={
                "status": old_status,
            },
            new_value={
                "status": task.status,
            },
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            entity_type="TASK",
            entity_id=instance.id,
            entity_name=instance.title,
            action=AuditLog.Action.DELETE,
        )

        instance.delete()