from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "started_date",
            "deadline",
            "finished_date",
            "project",
            "assigned_to",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "project",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "finished_date",
        ]

    def validate(self, attrs):

        project = attrs.get("project")

        if project is None and self.instance:
            project = self.instance.project

        assigned_to = attrs.get("assigned_to")

        if assigned_to is None and self.instance:
            assigned_to = self.instance.assigned_to

        # بررسی عضویت Assigned User
        if assigned_to:
            if not project.workspace.members.filter(
                id=assigned_to.id
            ).exists() and project.workspace.owner != assigned_to:

                raise serializers.ValidationError({
                    "assigned_to": (
                        "کاربر انتخاب‌شده عضو "
                        "ورک‌اسپیس پروژه نیست."
                    )
                })

        started_date = attrs.get("started_date")

        if started_date is None and self.instance:
            started_date = self.instance.started_date

        deadline = attrs.get("deadline")

        if deadline is None and self.instance:
            deadline = self.instance.deadline

        finished_date = attrs.get("finished_date")

        if started_date and deadline:
            if deadline < started_date:
                raise serializers.ValidationError({
                    "deadline": (
                        "مهلت انجام نمی‌تواند "
                        "قبل از تاریخ شروع باشد."
                    )
                })

        if started_date and finished_date:
            if finished_date < started_date:
                raise serializers.ValidationError({
                    "finished_date": (
                        "تاریخ پایان نمی‌تواند "
                        "قبل از تاریخ شروع باشد."
                    )
                })

        return attrs