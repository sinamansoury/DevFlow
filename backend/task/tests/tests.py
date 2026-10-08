from datetime import datetime, timezone


import pytest
from rest_framework import status

from task.models import Task
from audit.models import AuditLog

from backend.conftest import owner


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, should_see_tasks",
    [
        ("owner", True),
        ("member", True),
        ("stranger", False)
    ]
)

def test_user_task_list(request, api_client, user_fixture, should_see_tasks, task):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.get(
        '/api/tasks/'
    )

    assert response.status_code == 200
    task_ids = {
        item['id']
        for item in response.data['results']
    }
    assert (task.id in task_ids) is should_see_tasks

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 201),
        ("member", 403),
        ("stranger", 403)
    ]
)

def test_user_task_create(request, api_client, user_fixture, expected_status ,project ,member):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.post(
        f'/api/tasks/projects/{project.id}/',
            {
                "title": "string",
                "description": "string",
                "status": "TODO",
                "started_date": "2026-10-07T22:50:29Z",
                "deadline": "2026-10-10T22:50:29Z",
                "assigned_to": member.id,
            },
            format = 'json'
    )
    assert response.status_code == expected_status
    if expected_status == 201:
        created_task = Task.objects.get(
            id=response.data['id']
        )

        assert created_task.project_id == project.id
        assert AuditLog.objects.filter(
            user=user,
            entity_type="TASK",
            entity_id=created_task.id,
            entity_name=created_task.title,
            action=AuditLog.Action.CREATE,
        ).exists()

@pytest.mark.django_db
def test_task_create_rejects_deadline_before_started_date(api_client, owner, project):
    api_client.force_authenticate(owner)

    initial_task_count = Task.objects.count()

    response = api_client.post(
        f'/api/tasks/projects/{project.id}/',
        {
            "title": "string",
            "description": "string",
            "status": "TODO",
            "started_date": "2026-10-07T22:50:29Z",
            "deadline": "2026-10-06T22:50:29Z",
            "assigned_to": owner.id,
        },
        format='json'
    )

    assert response.status_code == 400
    assert Task.objects.count() == initial_task_count
    assert not AuditLog.objects.filter(
        entity_type="TASK",
        user_id=owner.id,
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

def test_user_task_list_retrieve(request, api_client, user_fixture, expected_status, task):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.get(
        f'/api/tasks/{task.id}/'
    )

    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.data["id"] == task.id
        assert response.data["title"] == task.title

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner" , 200),
        ("member" , 403),
        ("stranger" , 404)
    ]
)

def test_user_task_patch(request, api_client, user_fixture, expected_status, task):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.patch(
        f'/api/tasks/{task.id}/',
        {
            "title": "string",
        },
        format='json'
    )
    assert response.status_code == expected_status

    if response.status_code == 200:
        updated_task = Task.objects.get(
            id=response.data['id']
        )
        assert response.data["id"] == updated_task.id
        assert updated_task.title == "string"
        assert updated_task.finished_date is None
        assert updated_task.updated_by == user
        assert AuditLog.objects.filter(
            entity_type="TASK",
            entity_id=updated_task.id,
            user_id=user.id,
            action=AuditLog.Action.UPDATE,
            entity_name="string",
            old_value={"title": task.title},
            new_value={"title": "string"},
        ).exists()

@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner", 200),
        ("member", 200),
        ("stranger", 404),
    ],
)
def test_user_task_patch_status(
    request,
    api_client,
    user_fixture,
    expected_status,
    task,
):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.patch(
        f"/api/tasks/{task.id}/",
        {
            "status": "DONE",
        },
        format="json",
    )

    assert response.status_code == expected_status

    if response.status_code == 200:
        updated_task = Task.objects.get(
            id=response.data["id"]
        )

        assert response.data["id"] == updated_task.id
        assert updated_task.title == task.title
        assert updated_task.status == "DONE"
        assert updated_task.finished_date is not None
        assert updated_task.updated_by == user

        if user == task.project.workspace.owner:

            assert AuditLog.objects.filter(
                entity_type="TASK",
                entity_id=updated_task.id,
                user_id=user.id,
                action=AuditLog.Action.UPDATE,
                entity_name=updated_task.title,
                old_value={
                    "status": "TODO",
                    "finished_date": None,
                },
                new_value={
                    "status": "DONE",
                    "finished_date": updated_task.finished_date.isoformat(),
                },
            ).exists()

        else:

            assert AuditLog.objects.filter(
                entity_type="TASK",
                entity_id=updated_task.id,
                user_id=user.id,
                action=AuditLog.Action.UPDATE_STATUS,
                entity_name=updated_task.title,
                old_value={
                    "status": "TODO",
                },
                new_value={
                    "status": "DONE",
                },
            ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "user_fixture, expected_status",
    [
        ("owner" , 200),
        ("member" , 403),
        ("stranger" , 404)
    ]
)

def test_user_task_put(request, api_client, user_fixture, expected_status, task,  member):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.put(
        f'/api/tasks/{task.id}/',
        {
            "title": "string",
            "description": "string",
            "status": "TODO",
            "started_date": "2026-10-07T22:50:29Z",
            "deadline": "2026-10-10T22:50:29Z",
            "assigned_to": member.id,
        },
        format='json'
    )
    assert response.status_code == expected_status

    if response.status_code == 200:
        updated_task = Task.objects.get(
            id=response.data['id']
        )
        assert response.data["id"] == updated_task.id
        assert updated_task.title == "string"
        assert updated_task.finished_date is None
        assert updated_task.updated_by == user
        assert AuditLog.objects.filter(
            entity_type="TASK",
            entity_id=updated_task.id,
            user_id=user.id,
            action=AuditLog.Action.UPDATE,
            entity_name="string",
        ).exists()

@pytest.mark.django_db
def test_user_task_put_without_requires(owner, api_client, task):

    api_client.force_authenticate(owner)

    response = api_client.put(
        f'/api/tasks/{task.id}/',
        {
            "title": "string",
            "description": "string",
        },
        format='json'
    )
    assert response.status_code == 400
    task.refresh_from_db()
    assert task.title == "string"
    assert task.finished_date is None
    assert task.description == "string"
    assert not AuditLog.objects.filter(
            entity_type="TASK",
            entity_id=task.id,
            user_id=owner.id,
            action=AuditLog.Action.UPDATE,
            entity_name="string",
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
def test_user_task_delete(request, api_client, user_fixture, expected_status, task):
    user = request.getfixturevalue(user_fixture)
    api_client.force_authenticate(user)

    response = api_client.delete(
        f'/api/tasks/{task.id}/'
    )

    assert response.status_code == expected_status

    if expected_status == 204:
        assert not  Task.objects.filter(id=task.id).exists()
        assert AuditLog.objects.filter(
            entity_type="TASK",
            entity_id=task.id,
            action=AuditLog.Action.DELETE,
            user_id=user.id,
            entity_name=task.title,
        ).exists()

