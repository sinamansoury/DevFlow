from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from project.models import Project


class IsTaskWorkspaceMember(BasePermission):
    """
    کاربر باید عضو Workspace مربوط به Task باشد
    یا Owner آن Workspace باشد.
    """

    def has_object_permission(self, request, view, obj):
        workspace = obj.project.workspace

        return (
            workspace.owner == request.user
            or workspace.members.filter(
                id=request.user.id
            ).exists()
        )


class IsTaskWorkspaceOwner(BasePermission):

    def has_permission(self, request, view):
        project_id = view.kwargs.get("project_id")

        if project_id is None:
            return True

        project = get_object_or_404(
            Project,
            id=project_id,
        )

        return project.workspace.owner == request.user

    def has_object_permission(self, request, view, obj):
        return obj.project.workspace.owner == request.user


class IsTaskOwnerOrAssignedUser(BasePermission):
    """
    Owner Workspace یا کسی که Task به او Assign شده.
    """

    def has_object_permission(self, request, view, obj):
        workspace = obj.project.workspace

        return (
            workspace.owner == request.user
            or obj.assigned_to == request.user
        )