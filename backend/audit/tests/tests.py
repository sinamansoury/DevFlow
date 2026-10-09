import pytest
from audit.models import AuditLog
from workspace.models import Workspace
from users.models import User
from datetime import date, datetime, time, timezone
from decimal import Decimal
from uuid import UUID
from audit.utils import make_json_safe



@pytest.mark.django_db
def test_owner_can_see_own_workspace_project_and_task_logs(api_client, owner, workspace, project, task):
    api_client.force_authenticate(user=owner)


    workspace_log = AuditLog.objects.create(
        user=owner,
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        entity_name=workspace.name,
        action="CREATE",
    )
    project_log = AuditLog.objects.create(
        user=owner,
        entity_type="PROJECT",
        entity_id=project.id,
        entity_name=project.name,
        action="CREATE",
    )
    task_log = AuditLog.objects.create(
        user=owner,
        entity_type="TASK",
        entity_id=task.id,
        entity_name=task.title,
        action="CREATE",
    )

    response = api_client.get("/api/audits/")

    assert response.status_code == 200

    returned_ids = {
        item["id"] for item in response.data["results"]
    }

    assert {
        workspace_log.id,
        project_log.id,
        task_log.id,
    }.issubset(returned_ids)

@pytest.mark.django_db
def test_member_cannot_see_workspace_logs(api_client, owner, member, workspace):

    api_client.force_authenticate(user=member)


    log = AuditLog.objects.create(
        user=owner,
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        entity_name=workspace.name,
        action="CREATE",
    )

    response = api_client.get("/api/audits/")

    assert response.status_code == 200
    assert log.id not in {
        item["id"] for item in response.data["results"]
    }

@pytest.mark.django_db
def test_owner_cannot_see_another_owners_logs(api_client, owner, workspace):
    another_owner = User.objects.create_user(
    email="another-owner@test.com",
    password="TestPassword123",
    )
    another_workspace = Workspace.objects.create(
    name="Another Workspace",
    description="Another description",
    owner=another_owner,
    )

    log = AuditLog.objects.create(
        user=another_owner,
        entity_type="WORKSPACE",
        entity_id=another_workspace.id,
        entity_name=another_workspace.name,
        action="CREATE",
    )


    api_client.force_authenticate(user=owner)

    response = api_client.get("/api/audits/")

    assert response.status_code == 200
    assert log.id not in {
        item["id"] for item in response.data["results"]
    }

@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_audit_logs(api_client):
    response = api_client.get("/api/audits/")

    assert response.status_code == 401

@pytest.mark.django_db
def test_filter_audit_logs_by_entity_type(api_client,owner, workspace, project):

    api_client.force_authenticate(user=owner)

    workspace_log = AuditLog.objects.create(
        user=owner,
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        entity_name=workspace.name,
        action="CREATE",
    )
    AuditLog.objects.create(
        user=owner,
        entity_type="PROJECT",
        entity_id=project.id,
        entity_name=project.name,
        action="CREATE",
    )

    response = api_client.get("/api/audits/?entity_type=WORKSPACE")

    assert response.status_code == 200
    results = response.data["results"]

    assert all(item["entity_type"] == "WORKSPACE" for item in results)
    assert workspace_log.id in {item["id"] for item in results}

@pytest.mark.django_db
def test_filter_audit_logs_by_action(api_client, owner, workspace):
    api_client.force_authenticate(user=owner)

    create_log = AuditLog.objects.create(
        user=owner,
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        entity_name=workspace.name,
        action="CREATE",
    )
    AuditLog.objects.create(
        user=owner,
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        entity_name=workspace.name,
        action="UPDATE",
    )

    response = api_client.get("/api/audits/?action=CREATE")

    assert response.status_code == 200
    results = response.data["results"]

    assert all(item["action"] == "CREATE" for item in results)
    assert create_log.id in {item["id"] for item in results}

@pytest.mark.parametrize(
    "value",
    [
    None,
    "DevFlow",
    123,
    12.5,
    True,
    False,
    ],
    )
def test_make_json_safe_preserves_json_primitive_values(value):
    assert make_json_safe(value) == value

def test_make_json_safe_converts_datetime_to_isoformat():
    value = datetime(2026, 10, 9, 12, 30, tzinfo=timezone.utc)

    assert make_json_safe(value) == "2026-10-09T12:30:00+00:00"

def test_make_json_safe_converts_date_to_isoformat():
    value = date(2026, 10, 9)

    assert make_json_safe(value) == "2026-10-09"

def test_make_json_safe_converts_time_to_isoformat():
    value = time(14, 25, 30)

    assert make_json_safe(value) == "14:25:30"

def test_make_json_safe_converts_decimal_to_string():
    value = Decimal("125.50")

    assert make_json_safe(value) == "125.50"

def test_make_json_safe_converts_uuid_to_string():
    value = UUID("12345678-1234-5678-1234-567812345678")

    assert make_json_safe(value) == "12345678-1234-5678-1234-567812345678"

@pytest.mark.django_db
def test_make_json_safe_converts_django_model_to_primary_key(owner):
    workspace = Workspace.objects.create(
    name="Test Workspace",
    description="Test description",
    owner=owner,
    )

    assert make_json_safe(workspace) == workspace.pk

def test_make_json_safe_converts_nested_dictionary():
    value = {
    "name": "DevFlow",
    "created": date(2026, 10, 9),
    "metadata": {
        "price": Decimal("99.90"),
    },
    }

    assert make_json_safe(value) == {
        "name": "DevFlow",
        "created": "2026-10-09",
        "metadata": {
            "price": "99.90",
        },
    }

def test_make_json_safe_converts_lists_tuples_and_sets():
    assert make_json_safe((1, 2)) == [1, 2]
    assert make_json_safe([1, Decimal("2.5")]) == [1, "2.5"]
    assert make_json_safe({1, 2}) in ([1, 2], [2, 1])

def test_make_json_safe_converts_dictionary_keys_to_strings():
    value = {
    1: "one",
    2: "two",
    }

    assert make_json_safe(value) == {
        "1": "one",
        "2": "two",
    }

def test_make_json_safe_raises_type_error_for_unsupported_value():
    value = object()

    with pytest.raises(
        TypeError,
        match="Unsupported value for AuditLog JSONField: object",
    ):
        make_json_safe(value)

@pytest.mark.django_db
def test_deleted_task_log_stays_visible_to_owner(api_client, owner, task):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(f"/api/tasks/{task.id}/")
    assert response.status_code == 204

    response = api_client.get("/api/audits/?action=DELETE&entity_type=TASK")

    assert response.status_code == 200
    assert [item["entity_id"] for item in response.data["results"]] == [task.id]


@pytest.mark.django_db
def test_deleted_project_log_stays_visible_to_owner(api_client, owner, project):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(f"/api/projects/{project.id}/")
    assert response.status_code == 204

    response = api_client.get("/api/audits/?action=DELETE&entity_type=PROJECT")

    assert [item["entity_id"] for item in response.data["results"]] == [project.id]


@pytest.mark.django_db
def test_logs_of_deleted_workspace_stay_visible_to_owner_only(
    api_client, owner, member, workspace, project
):
    api_client.force_authenticate(user=owner)
    api_client.delete(f"/api/projects/{project.id}/")
    workspace_id = workspace.id
    response = api_client.delete(f"/api/workspaces/{workspace_id}/")
    assert response.status_code == 204

    response = api_client.get("/api/audits/")
    assert {
        (item["entity_type"], item["action"])
        for item in response.data["results"]
    } >= {("PROJECT", "DELETE"), ("WORKSPACE", "DELETE")}

    api_client.force_authenticate(user=member)
    assert api_client.get("/api/audits/").data["results"] == []
