import pytest


@pytest.mark.django_db
def test_unauthenticated_error_has_standard_format(api_client):
    response = api_client.get("/api/workspaces/")

    assert response.status_code == 401
    assert response.data["success"] is False
    assert response.data["status_code"] == 401
    assert isinstance(response.data["message"], str)
    assert response.data["errors"] is None

@pytest.mark.django_db
def test_permission_denied_error_has_standard_format(api_client,member,workspace,):
    api_client.force_authenticate(user=member)

    response = api_client.patch(
        f"/api/workspaces/{workspace.id}/",
        {"name": "Changed"},
        format="json",
    )

    assert response.status_code == 403
    assert response.data["success"] is False
    assert response.data["status_code"] == 403
    assert isinstance(response.data["message"], str)
    assert response.data["errors"] is None

@pytest.mark.django_db
def test_validation_error_preserves_field_errors(api_client,owner,workspace,):
    api_client.force_authenticate(user=owner)

    response = api_client.post(
        f"/api/workspaces/{workspace.id}/members/add/",
        {"email": "invalid-email"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["success"] is False
    assert response.data["status_code"] == 400
    assert response.data["message"] == "درخواست نامعتبر است."
    assert "email" in response.data["errors"]

@pytest.mark.django_db
def test_not_found_error_has_standard_format(api_client,stranger,workspace,):
    api_client.force_authenticate(user=stranger)

    response = api_client.get(
        f"/api/workspaces/{workspace.id}/",
    )

    assert response.status_code == 404
    assert response.data["success"] is False
    assert response.data["status_code"] == 404
    assert isinstance(response.data["message"], str)
    assert response.data["errors"] is None

