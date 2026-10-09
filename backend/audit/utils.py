from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from django.db.models import Model

from .models import AuditLog


def make_json_safe(value):
    """
    Convert common Django/Python values to JSON-compatible values
    before storing them in AuditLog JSONFields.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (datetime, date, time)):
        return value.isoformat()

    if isinstance(value, (Decimal, UUID)):
        return str(value)

    if isinstance(value, Model):
        return value.pk

    if isinstance(value, dict):
        return {
            str(key): make_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]

    raise TypeError(
        f"Unsupported value for AuditLog JSONField: {type(value).__name__}"
    )


def log_action(
    *,
    user,
    entity_type,
    entity_id,
    entity_name,
    action,
    workspace_id=None,
    old_value=None,
    new_value=None,
):
    """Create an AuditLog row. Call inside the same transaction as the change."""
    return AuditLog.objects.create(
        user=user,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        action=action,
        workspace_id=workspace_id,
        old_value=old_value,
        new_value=new_value,
    )
