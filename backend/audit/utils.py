from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from django.db.models import Model


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
