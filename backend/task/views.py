from django.utils import timezone
from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from audit.models import AuditLog
from .models import Task
from .permissions import IsTaskWorkspaceMember, IsTaskWorkspaceOwner
from .serializers import TaskSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

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

    def get_queryset(self):
        return (
            Task.objects.select_related(
                 "project",
                 "project__workspace",
                 "assigned_to",
                 "created_by",
                 "updated_by",
            )
            .filter(
                Q(project__workspace__owner=self.request.user)
                | Q(project__workspace__members=self.request.user)
            ).distinct()
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


class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer

    lookup_url_kwarg = "id"

    def get_permissions(self):
        if self.request.method == "DELETE":
            permission_classes = [
                IsAuthenticated,
                IsTaskWorkspaceOwner
            ]
        else:
            permission_classes = [
                IsAuthenticated,
                IsTaskWorkspaceMember
            ]

        return [
            permission()
            for permission in permission_classes
        ]

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


        serializer.validated_data.pop("finished_date", None)

        new_status = serializer.validated_data.get(
            "status",
            task.status
        )

        extra_data = {}

        if new_status == "DONE" and task.status != "DONE":
            extra_data["finished_date"] = timezone.now()

        elif new_status != "DONE" and task.finished_date:
            extra_data["finished_date"] = None

        if workspace.owner == self.request.user:

            old_value = {
                field: make_json_safe(getattr(task, field))
                for field in serializer.validated_data.keys()
            }

            serializer.save(
                updated_by=self.request.user,
                **extra_data
            )

            task.refresh_from_db()

            new_value = {
                field: make_json_safe(getattr(task, field))
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
            **extra_data
        )

        task.refresh_from_db()

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="TASK",
            entity_id=task.id,
            entity_name=task.title,
            action=AuditLog.Action.UPDATE_STATUS,
            old_value={
                "status": old_status
            },
            new_value={
                "status": task.status
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