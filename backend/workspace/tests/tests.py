import pytest
from workspace.models import Workspace
from audit.models import AuditLog


@pytest.mark.django_db
def test_authenticated_user_can_create_workspace(user, api_client):
    api_client.force_authenticate(user=user)

    response = api_client.post(
        "/api/workspaces/",
        {
            "name": "New Workspace",
            "description": "Test workspace",
        },
        format = "json"
    )

    assert response.status_code == 201

    workspace = Workspace.objects.get(name="New Workspace")

    assert workspace.owner == user
    assert workspace.members.filter(id=user.id).exists()

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.CREATE,
        user_id=user.id,
        entity_name=workspace.name,
    ).exists()

@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_workspace(user, api_client):
    response = api_client.post(
        "/api/workspaces/",
        {
            "name": "New Workspace",
            "description": "Test workspace",
        },
        format="json"
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_owner_can_retrieve_workspace(owner, workspace, api_client):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 200
    assert response.data["id"] == workspace.id

@pytest.mark.django_db
def test_member_can_retrieve_workspace(member, workspace,api_client):
    api_client.force_authenticate(user=member)

    response = api_client.get(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 200
    assert response.data["id"] == workspace.id

@pytest.mark.django_db
def test_stranger_cannot_retrieve_workspace(stranger, workspace,api_client):
    api_client.force_authenticate(user=stranger)

    response = api_client.get(
        f"/api/workspaces/{workspace.id}/",
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_owner_can_update_workspace(owner, workspace, api_client):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
        },
        format= "json"
    )

    assert response.status_code == 200
    workspace.refresh_from_db()
    assert workspace.name == "Updated Workspace"

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.UPDATE,
        user_id=owner.id,
    ).exists()

@pytest.mark.django_db
def test_member_cannot_update_workspace(member, workspace,api_client):
    api_client.force_authenticate(user=member)

    response = api_client.patch(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
        },
        format= "json"
    )

    assert response.status_code == 403
    workspace.refresh_from_db()
    assert workspace.name == "Test Workspace"

@pytest.mark.django_db
def test_owner_can_delete_workspace(owner, workspace, api_client):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 204
    assert not Workspace.objects.filter(id=workspace.id).exists()

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.DELETE,
        user_id=owner.id,
    ).exists()

@pytest.mark.django_db
def test_member_cannot_delete_workspace(member, workspace, api_client):
    api_client.force_authenticate(user=member)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 403
    assert Workspace.objects.filter(id=workspace.id).exists()

@pytest.mark.django_db
def test_stranger_cannot_delete_workspace(stranger, workspace, api_client):
    api_client.force_authenticate(user=stranger)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 404
    assert Workspace.objects.filter(id=workspace.id).exists()

@pytest.mark.django_db
def test_owner_can_list_own_workspaces(owner, workspace,api_client):
    api_client.force_authenticate(user=owner)

    response = api_client.get(
        "/api/workspaces/"
    )

    assert response.status_code == 200

    workspace_ids = [
        item["id"]
        for item in response.data["results"]
    ]

    assert workspace.id in workspace_ids

@pytest.mark.django_db
def test_stranger_cannot_see_workspace_in_list(stranger, workspace,api_client):
    api_client.force_authenticate(user=stranger)

    response = api_client.get("/api/workspaces/")

    assert response.status_code == 200

    workspace_ids = [
        item["id"]
        for item in response.data["results"]
    ]

    assert workspace.id not in workspace_ids




