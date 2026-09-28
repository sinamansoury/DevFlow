from rest_framework import serializers

from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    workspace_name = serializers.CharField(
        source="workspace.name",
        read_only=True
    )
    class Meta:
        model = Project
        fields = "__all__"

        read_only_fields = [
            "id",
            "workspace",
            "created_at",
            "updated_at",
        ]


