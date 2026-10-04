import pytest
from unittest.mock import patch

from project.models import Project

from audit.models import AuditLog

from backend.conftest import workspace


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
def test_project_create_with_nonexistent_workspace(api_client,owner,):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        "/api/projects/workspace/999999/",
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
