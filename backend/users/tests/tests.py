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
    assert "password" not in response.data

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

@pytest.mark.django_db
def test_register_with_duplicate_email(api_client, user):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": user.email,
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 400

@pytest.mark.django_db
def test_login_with_wrong_password(api_client, user):
    response = api_client.post(
        "/api/auth/login/",
        {
            "email": user.email,
            "password": "WrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_authenticated_user_can_get_me(api_client, user):
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.data["id"] == user.id
    assert response.data["email"] == user.email
    assert "password" not in response.data