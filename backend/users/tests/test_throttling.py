import pytest
from rest_framework.throttling import SimpleRateThrottle


@pytest.fixture
def throttle_rates(monkeypatch):
    """
    DRF reads DEFAULT_THROTTLE_RATES once, when the throttle class is
    defined, so override_settings has no effect. Patch the class attribute.
    """

    def _set(**rates):
        monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)

    return _set


@pytest.mark.django_db
def test_login_is_throttled_after_rate_limit(api_client, throttle_rates):
    throttle_rates(login="2/min", register="10/hour")
    payload = {
        "email": "unknown@example.com",
        "password": "WrongPassword123!",
    }

    statuses = [
        api_client.post("/api/auth/login/", payload, format="json").status_code
        for _ in range(3)
    ]

    assert statuses == [401, 401, 429]


@pytest.mark.django_db
def test_register_is_throttled_after_rate_limit(api_client, throttle_rates):
    throttle_rates(login="10/min", register="2/hour")

    statuses = [
        api_client.post("/api/auth/register/", {}, format="json").status_code
        for _ in range(3)
    ]

    assert statuses == [400, 400, 429]
