from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Project
from .serializers import ProjectSerializer
from audit.models import AuditLog
from django.db.models import Q
from .permissions import (
    IsProjectWorkspaceMember,
    IsProjectWorkspaceOwner,
)


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        "workspace",
    ]

    def get_queryset(self):
            return Project.objects.filter(
                Q(workspace__owner=self.request.user)
                | Q(workspace__members=self.request.user)
            ).distinct()

    def perform_create(self, serializer):
        workspace = serializer.validated_data["workspace"]

        if workspace.owner != self.request.user:
            raise PermissionDenied()

        project = serializer.save()

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="PROJECT",
            entity_id=project.id,
            entity_name=project.name,
            action=AuditLog.Action.CREATE,
        )


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "id"

    def get_permissions(self):

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [
                IsAuthenticated,
                IsProjectWorkspaceOwner,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
                IsProjectWorkspaceMember,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_queryset(self):
        return Project.objects.filter(
            Q(workspace__owner=self.request.user)
            | Q(workspace__members=self.request.user)
        ).distinct()

    def perform_update(self, serializer):
        project = serializer.instance

        old_value = {
            field: getattr(project, field)
            for field in serializer.validated_data.keys()
        }

        serializer.save()

        new_value = {
            field: value
            for field, value in serializer.validated_data.items()
        }

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="PROJECT",
            entity_id=project.id,
            entity_name=project.name,
            action=AuditLog.Action.UPDATE,
            old_value=old_value,
            new_value=new_value,
        )

    def perform_destroy(self, instance):

        project_id = instance.id
        project_name = instance.name

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="PROJECT",
            entity_id=project_id,
            entity_name=project_name,
            action=AuditLog.Action.DELETE,
        )

        instance.delete()




