from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from .models import Workspace



class IsWorkspaceMember(BasePermission):
    """
    Owner یا Member بتواند Workspace را ببیند.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user
            or obj.members.filter(
                id=request.user.id
            ).exists()
        )


class IsWorkspaceOwner(BasePermission):
    """
    فقط Owner اجازه تغییرات مدیریتی دارد.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsWorkspaceOwnerByUrl(BasePermission):
    """
    فقط Owner Workspace مربوط به URL اجازه دسترسی دارد.
    """

    def has_permission(self, request, view):
        workspace = get_object_or_404(
            Workspace,
            id=view.kwargs["workspace_id"],
        )

        return workspace.owner == request.user