from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Workspace
from .serializers import (
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    AddWorkspaceMemberSerializer,
)

from users.models import User
from audit.models import AuditLog

from .permissions import (
    IsWorkspaceMember,
    IsWorkspaceOwner,
)


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Workspace.objects.select_related(
                "owner",
            )
            .prefetch_related(
                "members",
            )
            .filter(
                Q(owner=self.request.user)
                | Q(members=self.request.user)
            ).distinct()
        )
    def perform_create(self, serializer):
        workspace = serializer.save(
            owner=self.request.user
        )

        workspace.members.add(
            self.request.user
        )

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="WORKSPACE",
            entity_id=workspace.id,
            entity_name=workspace.name,
            action=AuditLog.Action.CREATE,
        )


class WorkspaceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkspaceSerializer
    lookup_url_kwarg = "id"

    def get_permissions(self):

        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            permission_classes = [
                IsAuthenticated,
                IsWorkspaceOwner,
            ]

        else:
            permission_classes = [
                IsAuthenticated,
                IsWorkspaceMember,
            ]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_queryset(self):
        return (
            Workspace.objects.select_related(
                "owner",
            )
            .prefetch_related(
                "members",
            )
            .filter(
                Q(owner=self.request.user)
                | Q(members=self.request.user)
            ).distinct()
        )

    def perform_update(self, serializer):

        workspace = serializer.instance

        old_value = {
            field: getattr(workspace, field)
            for field in serializer.validated_data.keys()
        }

        serializer.save()

        new_value = {
            field: value
            for field, value in serializer.validated_data.items()
        }

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="WORKSPACE",
            entity_id=workspace.id,
            entity_name=workspace.name,
            action=AuditLog.Action.UPDATE,
            old_value=old_value,
            new_value=new_value,
        )

    def perform_destroy(self, instance):

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="WORKSPACE",
            entity_id=instance.id,
            entity_name=instance.name,
            action=AuditLog.Action.DELETE,
        )

        instance.delete()


class WorkspaceMemberListView(generics.ListAPIView):
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        if (
            workspace.owner != self.request.user
            and not workspace.members.filter(
                id=self.request.user.id
            ).exists()
        ):
            raise PermissionDenied()

        return workspace.members.all()


class WorkspaceMemberAddView(generics.CreateAPIView):
    serializer_class = AddWorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        if workspace.owner != self.request.user:
            raise PermissionDenied()

        user = User.objects.get(
            email=serializer.validated_data["email"]
        )

        workspace.members.add(user)

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="WORKSPACE",
            entity_id=workspace.id,
            entity_name=workspace.name,
            action=AuditLog.Action.ADD_MEMBER,
            new_value={
                "user_id": user.id,
                "email": user.email,
            },
        )


class WorkspaceMemberDeleteView(generics.DestroyAPIView):
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "user_id"

    def get_queryset(self):

        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        if workspace.owner != self.request.user:
            raise PermissionDenied()

        return workspace.members.all()

    def perform_destroy(self, instance):

        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        # جلوگیری از حذف Owner از Memberها
        if instance == workspace.owner:
            raise PermissionDenied()

        workspace.members.remove(instance)

        AuditLog.objects.create(
            user=self.request.user,
            entity_type="WORKSPACE",
            entity_id=workspace.id,
            entity_name=workspace.name,
            action=AuditLog.Action.REMOVE_MEMBER,
            old_value={
                "user_id": instance.id,
                "email": instance.email,
            },
        )