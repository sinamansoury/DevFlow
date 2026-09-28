from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

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
            "assigned_to_name",

            "created_by",
            "created_by_name",

            "updated_by",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "finished_date",
        ]


    def get_assigned_to_name(self, obj):
        if not obj.assigned_to:
            return None

        name = (
            f"{obj.assigned_to.first_name} "
            f"{obj.assigned_to.last_name}"
        ).strip()

        return name or obj.assigned_to.email


    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None

        name = (
            f"{obj.created_by.first_name} "
            f"{obj.created_by.last_name}"
        ).strip()

        return name or obj.created_by.email


    def validate(self, attrs):

        project = attrs.get("project")

        if project is None and self.instance:
            project = self.instance.project


        assigned_to = attrs.get("assigned_to")

        if assigned_to is None and self.instance:
            assigned_to = self.instance.assigned_to


        if assigned_to:

            if (
                not project.workspace.members.filter(
                    id=assigned_to.id
                ).exists()
                and project.workspace.owner != assigned_to
            ):
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