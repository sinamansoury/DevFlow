import pytest
from unittest.mock import patch

from project.models import Project

from audit.models import AuditLog


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, should_see_projects",
    [
        ("owner" , True),
        ("member" , True),
        ("stranger" , False)
    ]
)


def test_project_list_access(request,api_client, user_fixture, should_see_projects, project):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.get(
        "/api/projects/"
    )
    assert response.status_code == 200

    project_ids = {
        item["id"]
        for item in response.data["results"]
    }
    assert (project.id in project_ids) is should_see_projects

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner" , 201),
        ("member" , 403),
        ("stranger" , 403)
    ]
)

def test_project_create(request,api_client, user_fixture, expected_status, project):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)
    response = api_client.post(
        f"/api/projects/workspace/{project.workspace_id}/",
        {
            "name":project.name,
            "description":project.description,
        },
        format = 'json'
    )
    assert response.status_code == expected_status

    if expected_status == 201:
        created_project = Project.objects.get(
            id= response.data["id"]
        )
        assert created_project.workspace_id == project.workspace_id
        assert AuditLog.objects.filter(
            entity_type="PROJECT",
            entity_id=created_project.id,
            action=AuditLog.Action.CREATE,
            user_id=user.id,
            entity_name=created_project.name,
        ).exists()

@pytest.mark.django_db
def test_project_create_ignores_workspace_from_payload(api_client, workspace, owner):
    api_client.force_authenticate(owner)
    response = api_client.post(
        f"/api/projects/workspace/{workspace.id}/",
        {
            "name": "test",
            "description": "string",
            "workspace":45
        },
        format = 'json'
    )

    assert response.status_code == 201
    created_project = Project.objects.get(id=response.data["id"])
    assert created_project.workspace_id == workspace.id

@pytest.mark.django_db
def test_project_create_with_nonexistent_workspace(api_client,owner,):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        "/api/projects/workspace/1/",
        {
            "name": "Invalid Workspace Project",
            "description": "Should not be created",
        },
        format="json",
    )

    assert response.status_code == 404

    assert not Project.objects.filter(
        name="Invalid Workspace Project"
    ).exists()

    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_name="Invalid Workspace Project",
        action=AuditLog.Action.CREATE,
    ).exists()

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner" , 200),
        ("member" , 200),
        ("stranger" , 404)
    ]
)

def test_project_retrieve_access(request,api_client, user_fixture, expected_status, project):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.get(
        f"/api/projects/{project.id}/",
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.data["id"] == project.id
        assert response.data["name"] == project.name

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner" , 200),
        ("member" , 403),
        ("stranger" , 404)
    ]
)

def test_project_patch_access(request,api_client,user_fixture,expected_status,project,):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.patch(
        f"/api/projects/{project.id}/",
        {
            "name" : "Test Project2"
        },
        format = 'json'
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.data["id"] == project.id
        assert response.data["name"] == "Test Project2"
        assert AuditLog.objects.filter(
            entity_type="PROJECT",
            entity_id=project.id,
            action=AuditLog.Action.UPDATE,
            user_id=user.id,
            entity_name="Test Project2",
            old_value={"name": project.name},
            new_value={"name": "Test Project2"},
        ).exists()

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 200),
        ("member", 403),
        ("stranger", 404)
    ]
)
def test_project_put_access(request, api_client, user_fixture, expected_status, project, ):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.put(
        f"/api/projects/{project.id}/",
        {
            "name": "Test Project2",
            "description": "Updated description",
        },
        format="json",
    )

    assert response.status_code == expected_status

    if expected_status == 200:
        assert response.data["id"] == project.id
        assert response.data["description"] == "Updated description"
        assert response.data["name"] == "Test Project2"
        assert AuditLog.objects.filter(
            entity_type="PROJECT",
            entity_id=project.id,
            action=AuditLog.Action.UPDATE,
            user_id=user.id,
            entity_name="Test Project2",
            old_value={"name": project.name,"description": project.description},
            new_value={"name": "Test Project2","description": "Updated description"},
        ).exists()

@pytest.mark.django_db
def test_project_put_without_required_name( api_client, project, owner):
    api_client.force_authenticate(user=owner)

    response = api_client.put(
        f"/api/projects/{project.id}/",
        {
            "description": "Updated description",
        },
        format="json",
    )

    assert response.status_code == 400
    project.refresh_from_db()

    assert project.name == "Test Project"
    assert project.description == "Test Description"
    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_id=project.id,
        user_id=owner.id,
        action=AuditLog.Action.UPDATE,
        old_value={"description": project.description},
        new_value={"description": "Updated description"},
    ).exists()

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 204),
        ("member", 403),
        ("stranger", 404)
    ]
)

def test_project_delete_access(request,api_client, user_fixture, expected_status, project):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)
    response = api_client.delete(
        f"/api/projects/{project.id}/",
    )

    assert response.status_code == expected_status
    if expected_status == 204:
        assert not Project.objects.filter(id=project.id).exists()
        assert AuditLog.objects.filter(
            entity_type="PROJECT",
            entity_id=project.id,
            action=AuditLog.Action.DELETE,
            user_id=user.id,
            entity_name=project.name,
        ).exists()

@pytest.mark.django_db
def test_project_create_is_atomic(api_client,owner,workspace,):
    api_client.force_authenticate(user=owner)

    with patch(
        "project.views.AuditLog.objects.create",
        side_effect=Exception("Audit log failed"),
    ):
        with pytest.raises(Exception, match="Audit log failed"):
            api_client.post(
                f"/api/projects/workspace/{workspace.id}/",
                {
                    "name": "Atomic Project",
                    "description": "Test transaction",
                },
                format="json",
            )

    assert not Project.objects.filter(
        name="Atomic Project",
        workspace=workspace,
    ).exists()

    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_name="Atomic Project",
        action=AuditLog.Action.CREATE,
        user=owner,
    ).exists()

def test_project_patch_is_atomic(api_client,owner,project):
    api_client.force_authenticate(user=owner)

    with patch(
        "project.views.AuditLog.objects.create",
        side_effect=Exception("Audit log failed"),
    ):
        with pytest.raises(Exception, match="Audit log failed"):
            api_client.patch(
                f"/api/projects/{project.id}/",
                {
                    "name": "Atomic Project",
                },
                format="json",
            )

    project.refresh_from_db()

    assert project.name == "Test Project"
    assert project.description == "Test Description"

    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_name="Atomic Project",
        action=AuditLog.Action.UPDATE,
        user=owner,
    ).exists()

def test_project_put_is_atomic(api_client,owner,project):
    api_client.force_authenticate(user=owner)

    with patch(
        "project.views.AuditLog.objects.create",
        side_effect=Exception("Audit log failed"),
    ):
        with pytest.raises(Exception, match="Audit log failed"):
            api_client.put(
                f"/api/projects/{project.id}/",
                {
                    "name": "Atomic Project",
                    "description": "Test transaction",
                },
                format="json",
            )

    project.refresh_from_db()

    assert project.name == "Test Project"
    assert project.description == "Test Description"

    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_name="Atomic Project",
        action=AuditLog.Action.UPDATE,
        user=owner,
    ).exists()

def test_project_delete_is_atomic(api_client,owner,project):
    api_client.force_authenticate(user=owner)

    with patch(
        "project.views.AuditLog.objects.create",
        side_effect=Exception("Audit log failed"),
    ):
        with pytest.raises(Exception, match="Audit log failed"):
            api_client.delete(
                f"/api/projects/{project.id}/",
            )

    assert Project.objects.filter(
        id=project.id,
    ).exists()

    assert not AuditLog.objects.filter(
        entity_type="PROJECT",
        entity_name="Atomic Project",
        action=AuditLog.Action.DELETE,
        user=owner,
    ).exists()

