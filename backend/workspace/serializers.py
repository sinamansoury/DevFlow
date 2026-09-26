from rest_framework import serializers

from .models import Workspace
from users.models import User


class WorkspaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workspace

        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "owner",
            "members",
            "created_at",
            "updated_at",
        ]

class WorkspaceMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
        ]

class AddWorkspaceMemberSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "کاربری با این ایمیل وجود ندارد."
            )

        return value