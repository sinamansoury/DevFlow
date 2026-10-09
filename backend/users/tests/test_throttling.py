import pytest
from django.test import override_settings
from django.conf import settings
from rest_framework.settings import api_settings
from django.test.signals import setting_changed

BASE_REST_FRAMEWORK = {
    **settings.REST_FRAMEWORK,
    "DEFAULT_THROTTLE_RATES": {
        **settings.REST_FRAMEWORK.get("DEFAULT_THROTTLE_RATES", {}),
        "login": "2/min",
        "register": "2/hour",
    },
}
@pytest.fixture(autouse=True)
def reload_drf_settings():
    api_settings.reload()
    yield
    api_settings.reload()

@pytest.mark.django_db
@override_settings(REST_FRAMEWORK=BASE_REST_FRAMEWORK)
def test_login_is_throttled_after_rate_limit(api_client, clear_throttle_cache,reload_drf_settings):
    payload = {
        "email": "unknown@example.com",
        "password": "WrongPassword123!",
    }

    first_response = api_client.post(
        "/api/auth/login/",
        payload,
        format="json",
    )
    second_response = api_client.post(
        "/api/auth/login/",
        payload,
        format="json",
    )
    third_response = api_client.post(
        "/api/auth/login/",
        payload,
        format="json",
    )

    assert first_response.status_code == 401
    assert second_response.status_code == 401
    assert third_response.status_code == 429


@pytest.mark.django_db
@override_settings(REST_FRAMEWORK=BASE_REST_FRAMEWORK)
def test_register_is_throttled_after_rate_limit(api_client, clear_throttle_cache, reload_drf_settings):
    payload = {}

    first_response = api_client.post(
        "/api/auth/register/",
        payload,
        format="json",
    )
    second_response = api_client.post(
        "/api/auth/register/",
        payload,
        format="json",
    )
    third_response = api_client.post(
        "/api/auth/register/",
        payload,
        format="json",
    )

    assert first_response.status_code == 400
    assert second_response.status_code == 400
    assert third_response.status_code == 429

