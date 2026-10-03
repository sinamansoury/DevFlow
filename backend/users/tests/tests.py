import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
def test_register_user(api_client):

    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 201
    assert User.objects.filter(
        email="test@example.com"
    ).exists()

@pytest.mark.django_db
def test_login_user(api_client):
    User.objects.create_user(
        email="test@example.com",
        password="StrongPassword123!",
    )

    response = api_client.post(
        "/api/auth/login/",
        {
            "email": "test@example.com",
            "password": "StrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_me_requires_authentication(api_client):

    response = api_client.get("/api/auth/me/")

    assert response.status_code == 401
