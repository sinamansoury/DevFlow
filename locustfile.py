
import os

from locust import HttpUser, task, between


class DevFlowUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        email = os.environ.get("DEVFLOW_EMAIL")
        password = os.environ.get("DEVFLOW_PASSWORD")

        if not email or not password:
            raise RuntimeError(
                "Set DEVFLOW_EMAIL and DEVFLOW_PASSWORD first."
            )

        response = self.client.post(
            "/api/auth/login/",
            json={"email": email, "password": password},
            name="POST /api/auth/login/",
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Login failed: {response.status_code}"
            )

        token = response.json().get("access")
        if not token:
            raise RuntimeError("Access token missing from login response.")

        self.client.headers.update({
            "Authorization": f"Bearer {token}"
        })

    @task
    def list_tasks(self):
        self.client.get(
            "/api/tasks/",
            name="GET /api/tasks/",
        )