from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = (
            "id",
            "user",
            "entity_type",
            "entity_id",
            "entity_name",
            "action",
            "old_value",
            "new_value",
            "created_at",
        )
        read_only_fields = fields
