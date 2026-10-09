import pytest

from rest_framework.test import APIClient
from django.core.cache import cache
from users.models import User
from workspace.models import Workspace
from project.models import Project
from task.models import Task


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="user@test.com",
        password="TestPassword123",
        phone="09364587956"
    )


@pytest.fixture
def owner(db):
    return User.objects.create_user(
        email="owner@test.com",
        password="TestPassword123",
    )


@pytest.fixture
def member(db):
    return User.objects.create_user(
        email="member@test.com",
        password="TestPassword123",
    )

@pytest.fixture
def stranger():
    return User.objects.create_user(
        email="stranger@example.com",
        password="StrongPassword123!",

    )


@pytest.fixture
def workspace(owner, member):
    workspace = Workspace.objects.create(
        name="Test Workspace",
        description="Test description",
        owner=owner,
    )
    workspace.members.add(owner, member)
    return workspace


@pytest.fixture
def project(workspace):
    return Project.objects.create(
        name="Test Project",
        description="Test Description",
        workspace=workspace,
    )


@pytest.fixture
def task(project, owner, member):
    return Task.objects.create(
        title="Test Task",
        description="Test Description",
        project=project,
        assigned_to=member,
        created_by=owner,
        started_date="2026-10-01T10:00:00Z",
        deadline="2026-10-10T10:00:00Z",
    )


@pytest.fixture
def authenticated_client(api_client):
    def _authenticate(user):
        api_client.force_authenticate(user=user)
        return api_client

    return _authenticate

@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()