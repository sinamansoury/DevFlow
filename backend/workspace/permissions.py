from rest_framework.permissions import BasePermission


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