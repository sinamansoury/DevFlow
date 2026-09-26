from rest_framework.permissions import BasePermission


class IsProjectWorkspaceMember(BasePermission):
    """
    کاربر باید عضو Workspace پروژه باشد
    یا Owner آن Workspace باشد.
    """

    def has_object_permission(self, request, view, obj):
        workspace = obj.workspace

        return (
            workspace.owner == request.user
            or workspace.members.filter(
                id=request.user.id
            ).exists()
        )


class IsProjectWorkspaceOwner(BasePermission):
    """
    فقط Owner Workspace پروژه اجازه دارد.
    """

    def has_object_permission(self, request, view, obj):
        return obj.workspace.owner == request.user
