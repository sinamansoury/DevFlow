from rest_framework.permissions import BasePermission


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
    """
    فقط Owner Workspace اجازه دارد.
    """

    def has_object_permission(self, request, view, obj):
        workspace = obj.project.workspace

        return workspace.owner == request.user


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