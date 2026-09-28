import itertools
import os
from uuid import uuid4

from locust import HttpUser, between, task


class TaskForgeUser(HttpUser):
    wait_time = between(1, 3)
    api_prefix = "/api/v1"
    _credential_index = itertools.count()

    def on_start(self) -> None:
        self.workspace_id = os.environ["TASKFORGE_LOAD_WORKSPACE_ID"]
        self.project_id = os.environ["TASKFORGE_LOAD_PROJECT_ID"]
        credentials = self._load_credentials()
        email, password = credentials[next(self._credential_index) % len(credentials)]

        response = self.client.post(
            f"{self.api_prefix}/auth/login",
            json={"email": email, "password": password},
            name="POST /auth/login",
        )
        response.raise_for_status()
        self.csrf_token = response.json()["csrf_token"]

    @staticmethod
    def _load_credentials() -> list[tuple[str, str]]:
        raw_credentials = os.environ["TASKFORGE_LOAD_USERS"]
        credentials: list[tuple[str, str]] = []
        for raw_credential in raw_credentials.split(","):
            email, separator, password = raw_credential.partition(":")
            if not separator or not email or not password:
                raise ValueError(
                    "TASKFORGE_LOAD_USERS must contain email:password pairs"
                )
            credentials.append((email, password))
        if not credentials:
            raise ValueError("TASKFORGE_LOAD_USERS must not be empty")
        return credentials

    @task(7)
    def read_tasks(self) -> None:
        self.client.get(
            f"{self.api_prefix}/workspaces/{self.workspace_id}/projects/"
            f"{self.project_id}/tasks",
            params={"page_size": 20},
            name="GET /workspaces/{workspace_id}/projects/{project_id}/tasks",
        )

    @task(2)
    def create_task(self) -> None:
        self.client.post(
            f"{self.api_prefix}/workspaces/{self.workspace_id}/projects/"
            f"{self.project_id}/tasks",
            headers={"X-CSRF-Token": self.csrf_token},
            json={"title": f"load-test-{uuid4()}", "status": "todo"},
            name="POST /workspaces/{workspace_id}/projects/{project_id}/tasks",
        )

    @task(1)
    def create_and_check_export(self) -> None:
        response = self.client.post(
            f"{self.api_prefix}/workspaces/{self.workspace_id}/exports",
            headers={
                "X-CSRF-Token": self.csrf_token,
                "Idempotency-Key": str(uuid4()),
            },
            name="POST /workspaces/{workspace_id}/exports",
        )
        if response.status_code == 202:
            export_id = response.json()["id"]
            self.client.get(
                f"{self.api_prefix}/exports/{export_id}",
                name="GET /exports/{export_id}",
            )
