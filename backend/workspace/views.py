from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Workspace
from .serializers import (
    WorkspaceSerializer,
    WorkspaceMemberSerializer,
    AddWorkspaceMemberSerializer,
)
from users.models import User
from audit.models import AuditLog
from audit.utils import log_action, make_json_safe
from task.models import Task
from .permissions import (
    IsWorkspaceMember,
    IsWorkspaceOwner,
    IsWorkspaceOwnerByUrl,
)


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="لیست و ایجاد Workspace",
        description=(
            "نمایش Workspaceهای کاربر و ایجاد یک Workspace جدید. "
            "کاربر ایجادکننده به عنوان Owner و Member اضافه می‌شود."
        ),
        tags=["Workspace"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ایجاد Workspace",
        description=(
            "ایجاد یک Workspace جدید. "
            "کاربر واردشده به عنوان Owner تعیین می‌شود."
        ),
        tags=["Workspace"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Workspace.objects
            .select_related("owner")
            .prefetch_related("members")
            .filter(
                Q(owner=self.request.user) |
                Q(members=self.request.user)
            )
            .distinct()
        )


    def perform_create(self, serializer):
        with transaction.atomic():
            workspace = serializer.save(
                owner=self.request.user
            )

            workspace.members.add(
                self.request.user
            )

            log_action(
                user=self.request.user,
                entity_type="WORKSPACE",
                entity_id=workspace.id,
                entity_name=workspace.name,
                action=AuditLog.Action.CREATE,
                workspace_id=workspace.id,
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

    @extend_schema(
        summary="دریافت Workspace",
        description=(
            "نمایش اطلاعات Workspace برای Owner یا Member."
        ),
        tags=["Workspace"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش کامل Workspace",
        description=(
            "ویرایش کامل Workspace. فقط Owner مجاز است."
        ),
        tags=["Workspace"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش Workspace",
        description=(
            "ویرایش بخشی از اطلاعات Workspace. فقط Owner مجاز است."
        ),
        tags=["Workspace"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="حذف Workspace",
        description=(
            "حذف Workspace. فقط Owner مجاز است."
        ),
        tags=["Workspace"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Workspace.objects
            .select_related("owner")
            .prefetch_related("members")
            .filter(
                Q(owner=self.request.user)
                | Q(members=self.request.user)
            )
            .distinct()
        )

    def perform_update(self, serializer):
        workspace = serializer.instance

        old_value = make_json_safe({
            field: getattr(workspace, field)
            for field in serializer.validated_data.keys()
        })

        with transaction.atomic():
            serializer.save()

            new_value = make_json_safe({
                field: value
                for field, value in serializer.validated_data.items()
            })

            log_action(
                user=self.request.user,
                entity_type="WORKSPACE",
                entity_id=workspace.id,
                entity_name=workspace.name,
                action=AuditLog.Action.UPDATE,
                workspace_id=workspace.id,
                old_value=old_value,
                new_value=new_value,
            )

    def perform_destroy(self, instance):
        with transaction.atomic():
            log_action(
                user=self.request.user,
                entity_type="WORKSPACE",
                entity_id=instance.id,
                entity_name=instance.name,
                action=AuditLog.Action.DELETE,
                workspace_id=instance.id,
            )

            instance.delete()


class WorkspaceMemberListView(generics.ListAPIView):
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [
        IsAuthenticated,
        IsWorkspaceOwnerByUrl,
    ]

    @extend_schema(
        summary="لیست اعضای Workspace",
        description=(
            "نمایش اعضای یک Workspace. "
            "فقط Owner می‌تواند لیست اعضا را مشاهده کند."
        ),
        tags=["Workspace Members"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        return workspace.members.all()


class WorkspaceMemberAddView(generics.CreateAPIView):
    serializer_class = AddWorkspaceMemberSerializer
    permission_classes = [
        IsAuthenticated,
        IsWorkspaceOwnerByUrl,
    ]

    @extend_schema(
        summary="افزودن عضو به Workspace",
        description=(
            "افزودن یک کاربر به Workspace با استفاده از ایمیل. "
            "فقط Owner می‌تواند عضو اضافه کند."
        ),
        tags=["Workspace Members"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        user = User.objects.get(
            email=serializer.validated_data["email"]
        )

        if workspace.members.filter(id=user.id).exists():
            raise ValidationError({
                "email": "این کاربر قبلاً عضو Workspace است."
            })

        with transaction.atomic():
            workspace.members.add(user)

            log_action(
                user=self.request.user,
                entity_type="WORKSPACE",
                entity_id=workspace.id,
                entity_name=workspace.name,
                action=AuditLog.Action.ADD_MEMBER,
                workspace_id=workspace.id,
                new_value={
                    "user_id": user.id,
                    "email": user.email,
                },
            )


class WorkspaceMemberDeleteView(generics.DestroyAPIView):
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [
        IsAuthenticated,
        IsWorkspaceOwnerByUrl,
    ]
    lookup_url_kwarg = "user_id"

    @extend_schema(
        summary="حذف عضو از Workspace",
        description=(
            "حذف یک عضو از Workspace. "
            "فقط Owner مجاز است و Owner خودش قابل حذف نیست."
        ),
        tags=["Workspace Members"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        self.workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        return self.workspace.members.all()

    def perform_destroy(self, instance):
        if instance == self.workspace.owner:
            raise PermissionDenied()

        with transaction.atomic():
            self.workspace.members.remove(instance)

            # assigned_to is required, so hand the removed member's tasks
            # back to the workspace owner instead of leaving them orphaned.
            reassigned = Task.objects.filter(
                project__workspace=self.workspace,
                assigned_to=instance,
            ).update(assigned_to=self.workspace.owner)

            log_action(
                user=self.request.user,
                entity_type="WORKSPACE",
                entity_id=self.workspace.id,
                entity_name=self.workspace.name,
                action=AuditLog.Action.REMOVE_MEMBER,
                workspace_id=self.workspace.id,
                old_value={
                    "user_id": instance.id,
                    "email": instance.email,
                },
                new_value=(
                    {"reassigned_tasks": reassigned}
                    if reassigned
                    else None
                ),
            )