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
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 200),
        ("member", 200),
        ("stranger", 404),
    ],
)
def test_workspace_retrieve_access(request,api_client,workspace,user_fixture,expected_status,):
    user = request.getfixturevalue(user_fixture)

    api_client.force_authenticate(user=user)

    response = api_client.get(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == expected_status

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
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 204),
        ("member", 403),
        ("stranger", 404),
    ],
)
def test_workspace_delete_access(request,api_client,workspace,user_fixture,expected_status,):
    user = request.getfixturevalue(user_fixture)

    api_client.force_authenticate(user=user)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == expected_status

    if expected_status == 204:
        assert not Workspace.objects.filter(
            id=workspace.id
        ).exists()

        assert AuditLog.objects.filter(
            entity_type="WORKSPACE",
            entity_id=workspace.id,
            action=AuditLog.Action.DELETE,
            user_id=user.id,
        ).exists()

    else:
        assert Workspace.objects.filter(
            id=workspace.id
        ).exists()

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, should_see_workspace",
    [
        ("owner", True),
        ("member", True),
        ("stranger", False),
    ],
)
def test_workspace_list_access(request,api_client,workspace,user_fixture,should_see_workspace,):
    user = request.getfixturevalue(user_fixture)

    api_client.force_authenticate(user=user)

    response = api_client.get("/api/workspaces/")

    assert response.status_code == 200

    workspace_ids = [
        item["id"]
        for item in response.data["results"]
    ]

    assert (workspace.id in workspace_ids) is should_see_workspace

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 200),
        ("member", 403),
        ("stranger", 403),
    ]
)
def test_workspace_members_list_access(request,api_client,workspace,user_fixture,expected_status,owner,member,):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user=user)
    response = api_client.get(
        f"/api/workspaces/{workspace.id}/members/",
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        member_ids = {
            item['id']
            for item in response.data["results"]
        }
        assert member_ids == {owner.id, member.id}

@pytest.mark.django_db
def test_owner_can_add_member_to_workspace(api_client, owner, stranger, workspace):
    api_client.force_authenticate(user=owner)
    assert not workspace.members.filter(id=stranger.id).exists()

    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {
            "email": stranger.email
        },
        format="json",
    )

    assert response.status_code == 201
    assert workspace.members.filter(id=stranger.id).exists()

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.ADD_MEMBER,
        user_id=owner.id,
        entity_name=workspace.name,
        new_value={"user_id": stranger.id, "email": stranger.email},
    ).exists()

@pytest.mark.django_db
def test_owner_cannot_add_duplicate_member(api_client,owner,member,workspace):
    api_client.force_authenticate(user=owner)

    assert workspace.members.filter(id=member.id).exists()

    before = AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.ADD_MEMBER,
    ).count()

    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {"email": member.email},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["email"] == "این کاربر قبلاً عضو Workspace است."

    assert workspace.members.filter(id=member.id).exists()

    after = AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.ADD_MEMBER,
    ).count()

    assert after == before

@pytest.mark.django_db
def test_member_cannot_add_member_to_workspace(member, workspace, api_client, stranger):
    api_client.force_authenticate(user=member)
    assert not workspace.members.filter(id=stranger.id).exists()
    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {
            "email": stranger.email
        },
        format="json",
    )
    assert response.status_code == 403

@pytest.mark.django_db
def test_stranger_cannot_add_member_to_workspace(workspace, api_client, stranger):
    api_client.force_authenticate(user=stranger)
    assert not workspace.members.filter(id=stranger.id).exists()
    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {
            "email": stranger.email
        },
        format="json",
    )
    assert response.status_code == 403
    assert not workspace.members.filter(id=stranger.id).exists()

@pytest.mark.django_db
def test_owner_can_delete_member_from_workspace(api_client, owner, member, workspace):
    api_client.force_authenticate(user=owner)
    assert workspace.members.filter(id=member.id).exists()

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{member.id}/",
    )

    assert response.status_code == 204
    assert not workspace.members.filter(id=member.id).exists()

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.REMOVE_MEMBER,
        user_id=owner.id,
        entity_name=workspace.name,
        old_value={"user_id": member.id, "email": member.email},

    ).exists()

@pytest.mark.django_db
def test_owner_cannot_delete_themselves_from_workspace(api_client,owner,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{owner.id}/",
    )

    assert response.status_code == 403
    assert workspace.members.filter(id=owner.id).exists()

@pytest.mark.django_db
def test_member_cannot_delete_member_from_workspace(api_client,owner, member, workspace):
    api_client.force_authenticate(user=member)
    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{owner.id}/",
    )

    assert response.status_code == 403

@pytest.mark.django_db
def test_user_cannot_delete_member_from_workspace(api_client, stranger,member, workspace):
    api_client.force_authenticate(user=stranger)
    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{member.id}/",
    )
    assert response.status_code == 403

@pytest.mark.django_db
def test_owner_cannot_add_nonexistent_user(api_client,owner,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {"email": "notfound@test.com"},
        format="json",
    )

    assert response.status_code == 400
    assert "کاربری با این ایمیل وجود ندارد." in str(response.data)

    assert AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.ADD_MEMBER,
    ).count() == 0

@pytest.mark.django_db
def test_owner_can_put_workspace(api_client,owner,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.put(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
            "description": "Updated description",
        },
        format="json",
    )

    assert response.status_code == 200

    workspace.refresh_from_db()

    assert workspace.name == "Updated Workspace"
    assert workspace.description == "Updated description"

@pytest.mark.django_db
def test_member_cannot_put_workspace(api_client, member, workspace):
    api_client.force_authenticate(user=member)

    response = api_client.put(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Hacked Workspace",
            "description": "Hacked description",
        },
        format="json",
    )

    assert response.status_code == 403

    workspace.refresh_from_db()
    assert workspace.name == "Test Workspace"
    assert workspace.description == "Test description"

    assert not AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.UPDATE,
        user_id=member.id,
    ).exists()


@pytest.mark.django_db
def test_cannot_delete_non_member_from_workspace(api_client,owner,stranger,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{stranger.id}/",
    )

    assert response.status_code == 404

    assert not workspace.members.filter(id=stranger.id).exists()

    assert not AuditLog.objects.filter(
        entity_type="WORKSPACE",
        entity_id=workspace.id,
        action=AuditLog.Action.REMOVE_MEMBER,
        user_id=owner.id,
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "endpoint",
    [
        "members/",
        "members/add/",
    ],
)
def test_unauthenticated_user_cannot_access_workspace_member_endpoints(api_client,workspace,endpoint,):
    response = api_client.get(
        f"/api/workspaces/{workspace.id}/{endpoint}"
    ) if endpoint == "members/" else api_client.post(
        f"/api/workspaces/{workspace.id}/{endpoint}",
        {"email": "stranger@test.com"},
        format="json",
    )

    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cannot_delete_workspace_member(api_client,workspace,member,):
    response = api_client.delete(
        f"/api/workspaces/{workspace.id}/members/delete/{member.id}/",
    )

    assert response.status_code == 401
    assert workspace.members.filter(id=member.id).exists()


@pytest.mark.django_db
def test_owner_cannot_mass_assign_workspace_owner(api_client,owner,stranger,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
            "owner": stranger.id,
        },
        format="json",
    )

    assert response.status_code == 200

    workspace.refresh_from_db()

    assert workspace.owner == owner
    assert workspace.name == "Updated Workspace"


@pytest.mark.django_db
def test_owner_cannot_mass_assign_workspace_members(api_client,owner,member,stranger,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.patch(
        f"/api/workspaces/{workspace.id}/",
        {
            "name": "Updated Workspace",
            "members": [stranger.id],
        },
        format="json",
    )

    assert response.status_code == 200

    workspace.refresh_from_db()

    assert workspace.name == "Updated Workspace"
    assert workspace.owner == owner

    assert workspace.members.filter(id=owner.id).exists()
    assert workspace.members.filter(id=member.id).exists()
    assert not workspace.members.filter(id=stranger.id).exists()

