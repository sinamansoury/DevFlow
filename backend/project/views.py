from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Project
from .serializers import ProjectSerializer
from audit.models import AuditLog
from audit.utils import log_action, make_json_safe
from .permissions import (
    IsProjectWorkspaceMember,
    IsProjectWorkspaceOwner,
)
from workspace.permissions import IsWorkspaceOwnerByUrl
from workspace.models import Workspace


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


    filterset_fields = [
        "workspace",
    ]

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
    ]
    @extend_schema(
        summary="لیست پروژه‌ها",
        description=(
            "نمایش پروژه‌های Workspaceهایی که کاربر "
            "Owner یا Member آن‌هاست."
        ),
        tags=["Project"],
        parameters=[
            OpenApiParameter(
                name="workspace",
                description="فیلتر پروژه‌ها بر اساس Workspace ID",
                required=False,
                type=int,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "workspace",
            )
            .filter(
                Q(workspace__owner=self.request.user)
                | Q(workspace__members=self.request.user)
            )
            .distinct()
        )


class ProjectCreateView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [
        IsAuthenticated,
        IsWorkspaceOwnerByUrl
    ]
    lookup_url_kwarg = "id"

    @extend_schema(
        summary="ایجاد پروژه",
        description=(
                "ایجاد پروژه در یک Workspace. "
                "فقط Owner Workspace می‌تواند پروژه ایجاد کند."
        ),
        tags=["Project"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        workspace = get_object_or_404(
            Workspace,
            id=self.kwargs["workspace_id"],
        )

        with transaction.atomic():
            project = serializer.save(
                workspace=workspace
            )

            log_action(
                user=self.request.user,
                entity_type="PROJECT",
                entity_id=project.id,
                entity_name=project.name,
                action=AuditLog.Action.CREATE,
                workspace_id=workspace.id,
            )


class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    lookup_url_kwarg = "id"

    def get_permissions(self):
        if self.request.method in [
            "PUT",
            "PATCH",
            "DELETE",
        ]:
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

    @extend_schema(
        summary="دریافت پروژه",
        description=(
            "نمایش اطلاعات پروژه برای Owner یا Member "
            "Workspace."
        ),
        tags=["Project"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش کامل پروژه",
        description=(
            "ویرایش کامل پروژه. "
            "فقط Owner Workspace مجاز است."
        ),
        tags=["Project"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش پروژه",
        description=(
            "ویرایش بخشی از اطلاعات پروژه. "
            "فقط Owner Workspace مجاز است."
        ),
        tags=["Project"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="حذف پروژه",
        description=(
            "حذف پروژه. "
            "فقط Owner Workspace مجاز است."
        ),
        tags=["Project"],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Project.objects
            .select_related(
                "workspace",
            )
            .filter(
                Q(workspace__owner=self.request.user)
                | Q(workspace__members=self.request.user)
            )
            .distinct()
        )

    def perform_update(self, serializer):
        project = serializer.instance

        old_value = make_json_safe({
            field: getattr(project, field)
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
                entity_type="PROJECT",
                entity_id=project.id,
                entity_name=project.name,
                action=AuditLog.Action.UPDATE,
                workspace_id=project.workspace_id,
                old_value=old_value,
                new_value=new_value,
            )

    def perform_destroy(self, instance):
        project_id = instance.id
        project_name = instance.name

        with transaction.atomic():
            log_action(
                user=self.request.user,
                entity_type="PROJECT",
                entity_id=project_id,
                entity_name=project_name,
                action=AuditLog.Action.DELETE,
                workspace_id=instance.workspace_id,
            )

            instance.delete()

