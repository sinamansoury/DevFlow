import pytest
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
def test_register_user_with_weak_pass(api_client):

    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "weak@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(
        email="test@example.com"
    ).exists()
    assert "password" not in response.data

@pytest.mark.django_db
def test_register_user_with_common_pass(api_client):

    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "common@example.com",
            "password": "password",
            "first_name": "Test",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(
        email="test@example.com"
    ).exists()
    assert "password" not in response.data

@pytest.mark.django_db
def test_register_user_with_user_data_pass(api_client):

    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "test@example.com",
            "password": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 400
    assert not User.objects.filter(
        email="test@example.com"
    ).exists()
    assert "password" not in response.data

@pytest.mark.django_db
def test_register_with_email_case_insensitive_duplicate(api_client, user):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": user.email.upper(),
            "password": "StrongPassword123!",
            "first_name": "Another",
            "last_name": "User",
            "phone": "09123456789",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "email" in response.data["errors"]

@pytest.mark.django_db
def test_register_with_invalid_phone(api_client):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "phone@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test",
            "last_name": "User",
            "phone": "12345",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "phone" in response.data["errors"]

@pytest.mark.django_db
def test_register_with_duplicate_phone(api_client, user):
    response = api_client.post(
        "/api/auth/register/",
        {
            "email": "another@example.com",
            "password": "StrongPassword123!",
            "first_name": "Another",
            "last_name": "User",
            "phone": user.phone,
        },
        format="json",
    )

    assert response.status_code == 400
    assert "phone" in response.data["errors"]

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
def test_inactive_user_cannot_login(api_client):
    User.objects.create_user(
        email="inactive@example.com",
        password="StrongPassword123!",
        is_active=False,
    )

    response = api_client.post(
        "/api/auth/login/",
        {
            "email": "inactive@example.com",
            "password": "StrongPassword123!",
        },
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_refresh_token_success(api_client):
    User.objects.create_user(
        email="refresh@example.com",
        password="StrongPassword123!",
    )

    login_response = api_client.post(
        "/api/auth/login/",
        {
            "email": "refresh@example.com",
            "password": "StrongPassword123!",
        },
        format="json",
    )

    refresh_token = login_response.data["refresh"]

    response = api_client.post(
        "/api/auth/refresh/",
        {"refresh": refresh_token},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data

@pytest.mark.django_db
def test_refresh_with_invalid_token(api_client):
    response = api_client.post(
        "/api/auth/refresh/",
        {"refresh": "invalid-token"},
        format="json",
    )

    assert response.status_code == 401

@pytest.mark.django_db
def test_me_with_invalid_jwt(api_client):
    api_client.credentials(
        HTTP_AUTHORIZATION="Bearer invalid-token"
    )

    response = api_client.get("/api/auth/me/")

    assert response.status_code == 401

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