from dataclasses import dataclass
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from taskforge.config import Settings
from taskforge.main import create_app


@dataclass
class LoggedInUser:
    id: str
    email: str
    csrf_token: str


class FakeProjectSummaryCache:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}
        self.get_calls: list[str] = []
        self.set_calls: list[str] = []
        self.delete_calls: list[str] = []

    def key(self, workspace_id: str, project_id: str) -> str:
        return f"taskforge:v1:workspace:{workspace_id}:project:{project_id}:summary"

    def get(self, workspace_id: str, project_id: str) -> object | None:
        key = self.key(workspace_id, project_id)
        self.get_calls.append(key)
        return self.values.get(key)

    def set(self, summary: object) -> None:
        key = self.key(summary.workspace_id, summary.id)
        self.set_calls.append(key)
        self.values[key] = summary

    def delete_key(self, key: str) -> None:
        self.delete_calls.append(key)
        self.values.pop(key, None)


def make_settings(url: str) -> Settings:
    return Settings(
        environment="test",
        storage_backend="postgres",
        database_url=url,
        database_pool_size=2,
        database_max_overflow=0,
        database_pool_timeout_seconds=2,
    )


def make_cached_app(url: str, cache: FakeProjectSummaryCache):
    app = create_app(make_settings(url))
    app.state.project_summary_cache = cache
    return app


def register_and_login(client: TestClient, email: str) -> LoggedInUser:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-password"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-password"},
    )
    assert login.status_code == 200

    body = login.json()
    return LoggedInUser(
        id=body["user"]["id"],
        email=email,
        csrf_token=body["csrf_token"],
    )


def login_existing_user(client: TestClient, email: str) -> LoggedInUser:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-password"},
    )
    assert login.status_code == 200

    body = login.json()
    return LoggedInUser(
        id=body["user"]["id"],
        email=email,
        csrf_token=body["csrf_token"],
    )


def add_membership(
    database_url: str,
    user_id: str,
    workspace_id: str,
    role: str,
) -> None:
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO memberships (id, user_id, workspace_id, role)
                    VALUES (:id, :user_id, :workspace_id, :role)
                    """
                ),
                {
                    "id": str(uuid4()),
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "role": role,
                },
            )
    finally:
        engine.dispose()


def create_workspace(client: TestClient, owner: LoggedInUser) -> str:
    response = client.post(
        "/api/v1/workspaces",
        json={"name": "Owner workspace"},
        headers={"X-CSRF-Token": owner.csrf_token},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_membership(
    client: TestClient,
    workspace_id: str,
    actor: LoggedInUser,
    email: str,
    role: str = "member",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/memberships",
        json={"email": email, "role": role},
        headers={"X-CSRF-Token": actor.csrf_token},
    )
    assert response.status_code == 201
    return response.json()


def create_workspace_project(
    client: TestClient,
    workspace_id: str,
    user: LoggedInUser,
    name: str = "Launch plan",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/projects",
        json={"name": name},
        headers={"X-CSRF-Token": user.csrf_token},
    )
    assert response.status_code == 201
    return response.json()


def create_workspace_task(
    client: TestClient,
    workspace_id: str,
    project_id: str,
    user: LoggedInUser,
    title: str = "Draft checklist",
) -> dict[str, object]:
    response = client.post(
        f"/api/v1/workspaces/{workspace_id}/projects/{project_id}/tasks",
        json={"title": title},
        headers={"X-CSRF-Token": user.csrf_token},
    )
    assert response.status_code == 201
    return response.json()


def test_authenticated_user_can_create_workspace(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        user = register_and_login(client, "owner@example.com")

        response = client.post(
            "/api/v1/workspaces",
            json={"name": "Owner workspace"},
            headers={"X-CSRF-Token": user.csrf_token},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Owner workspace"


def test_outsider_cannot_list_workspace_projects(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)

        register_and_login(client, "outsider@example.com")

        response = client.get(f"/api/v1/workspaces/{workspace_id}/projects")

    assert response.status_code == 404


def test_owner_can_list_workspace_projects(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)

        response = client.get(f"/api/v1/workspaces/{workspace_id}/projects")

    assert response.status_code == 200
    assert response.json() == []


def test_owner_can_create_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)

        created = create_workspace_project(client, workspace_id, owner)
        listed = client.get(f"/api/v1/workspaces/{workspace_id}/projects")

    assert created["name"] == "Launch plan"
    assert listed.status_code == 200
    assert [project["name"] for project in listed.json()] == ["Launch plan"]


def test_outsider_cannot_create_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)

        outsider = register_and_login(client, "outsider@example.com")

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/projects",
            json={"name": "Intrusion"},
            headers={"X-CSRF-Token": outsider.csrf_token},
        )

    assert response.status_code == 404


def test_owner_can_read_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Launch plan"


def test_outsider_cannot_read_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        register_and_login(client, "outsider@example.com")

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
        )

    assert response.status_code == 404


def test_owner_can_update_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}",
            json={"name": "Updated launch plan"},
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated launch plan"


def test_outsider_cannot_update_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        outsider = register_and_login(client, "outsider@example.com")

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}",
            json={"name": "Intrusion"},
            headers={"X-CSRF-Token": outsider.csrf_token},
        )

    assert response.status_code == 404


def test_owner_can_delete_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        deleted = client.delete(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}",
            headers={"X-CSRF-Token": owner.csrf_token},
        )
        read_after_delete = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
        )

    assert deleted.status_code == 204
    assert read_after_delete.status_code == 404


def test_member_cannot_delete_workspace_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        member = register_and_login(client, "member@example.com")
        add_membership(migrated_database_url, member.id, workspace_id, "member")

        response = client.delete(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}",
            headers={"X-CSRF-Token": member.csrf_token},
        )

    assert response.status_code == 403


def test_owner_can_create_and_list_workspace_tasks(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        created = create_workspace_task(client, workspace_id, project["id"], owner)
        listed = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/tasks"
        )

    assert created["title"] == "Draft checklist"
    assert listed.status_code == 200
    assert [task["title"] for task in listed.json()] == ["Draft checklist"]


def test_owner_can_read_workspace_task(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}"
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Draft checklist"


def test_owner_can_read_workspace_project_summary(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        create_workspace_task(client, workspace_id, project["id"], owner)
        create_workspace_task(
            client, workspace_id, project["id"], owner, title="Review notes"
        )

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": project["id"],
            "workspace_id": workspace_id,
            "name": "Launch plan",
            "task_count": 2,
        }


def test_workspace_project_summary_counts_zero_tasks(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(
            client, workspace_id, owner, name="Empty project"
        )

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

    assert response.status_code == 200
    assert response.json()["task_count"] == 0


def test_outsider_cannot_read_workspace_project_summary(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        register_and_login(client, "outsider@example.com")

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

    assert response.status_code == 404


def test_workspace_project_summary_cache_miss_then_hit(
    migrated_database_url: str,
) -> None:
    cache = FakeProjectSummaryCache()

    with TestClient(make_cached_app(migrated_database_url, cache)) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        create_workspace_task(client, workspace_id, project["id"], owner)

        first = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )
        second = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert len(cache.get_calls) == 2
    assert len(cache.set_calls) == 1


def test_workspace_project_summary_cache_invalidates_after_task_create(
    migrated_database_url: str,
) -> None:
    cache = FakeProjectSummaryCache()

    with TestClient(make_cached_app(migrated_database_url, cache)) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        before = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )
        create_workspace_task(client, workspace_id, project["id"], owner)
        after = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

    expected_key = (
        f"taskforge:v1:workspace:{workspace_id}:project:{project['id']}:summary"
    )

    assert before.status_code == 200
    assert before.json()["task_count"] == 0
    assert after.status_code == 200
    assert after.json()["task_count"] == 1
    assert expected_key in cache.delete_calls


def test_outsider_cannot_read_cached_workspace_project_summary(
    migrated_database_url: str,
) -> None:
    cache = FakeProjectSummaryCache()

    with TestClient(make_cached_app(migrated_database_url, cache)) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)

        owner_read = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )
        register_and_login(client, "outsider@example.com")
        outsider_read = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}/summary"
        )

    assert owner_read.status_code == 200
    assert outsider_read.status_code == 404
    assert len(cache.set_calls) == 1


def test_owner_can_update_workspace_task(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}",
            json={
                "title": "Updated checklist",
                "status": "in_progress",
                "expected_version": task["version"],
            },
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated checklist"
    assert response.json()["status"] == "in_progress"


def test_workspace_task_update_keeps_status_transition_rule(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}",
            json={"status": "done", "expected_version": task["version"]},
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 409


def test_owner_can_delete_workspace_task(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        deleted = client.delete(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}",
            headers={"X-CSRF-Token": owner.csrf_token},
        )
        read_after_delete = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}"
        )

    assert deleted.status_code == 204
    assert read_after_delete.status_code == 404


def test_outsider_cannot_read_workspace_task_by_swapping_project_and_task(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        register_and_login(client, "outsider@example.com")

        response = client.get(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}"
        )

    assert response.status_code == 404


def test_user_cannot_read_foreign_task_under_own_project(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner_a = register_and_login(client, "owner-a@example.com")
        workspace_a_id = create_workspace(client, owner_a)
        project_a = create_workspace_project(client, workspace_a_id, owner_a)

        owner_b = register_and_login(client, "owner-b@example.com")
        workspace_b_id = create_workspace(client, owner_b)
        project_b = create_workspace_project(client, workspace_b_id, owner_b)
        task_b = create_workspace_task(client, workspace_b_id, project_b["id"], owner_b)

        login_existing_user(client, "owner-a@example.com")

        response = client.get(
            f"/api/v1/workspaces/{workspace_a_id}/projects/{project_a['id']}"
            f"/tasks/{task_b['id']}"
        )

    assert response.status_code == 404


def test_owner_can_add_and_list_workspace_membership(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        member = register_and_login(client, "member@example.com")
        owner = login_existing_user(client, "owner@example.com")

        created = create_membership(client, workspace_id, owner, member.email)
        listed = client.get(f"/api/v1/workspaces/{workspace_id}/memberships")

    assert created["email"] == "member@example.com"
    assert created["role"] == "member"
    assert listed.status_code == 200
    assert {membership["email"] for membership in listed.json()} == {
        "owner@example.com",
        "member@example.com",
    }


def test_admin_can_add_workspace_membership(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        admin = register_and_login(client, "admin@example.com")
        target = register_and_login(client, "target@example.com")
        owner = login_existing_user(client, "owner@example.com")
        create_membership(client, workspace_id, owner, admin.email, role="admin")
        admin = login_existing_user(client, "admin@example.com")

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/memberships",
            json={"email": target.email, "role": "member"},
            headers={"X-CSRF-Token": admin.csrf_token},
        )

    assert response.status_code == 201
    assert response.json()["email"] == "target@example.com"


def test_member_cannot_add_workspace_membership(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        member = register_and_login(client, "member@example.com")
        target = register_and_login(client, "target@example.com")
        owner = login_existing_user(client, "owner@example.com")
        create_membership(client, workspace_id, owner, member.email)
        member = login_existing_user(client, "member@example.com")

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/memberships",
            json={"email": target.email, "role": "member"},
            headers={"X-CSRF-Token": member.csrf_token},
        )

    assert response.status_code == 403


def test_outsider_cannot_add_workspace_membership(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        target = register_and_login(client, "target@example.com")
        outsider = register_and_login(client, "outsider@example.com")

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/memberships",
            json={"email": target.email, "role": "member"},
            headers={"X-CSRF-Token": outsider.csrf_token},
        )

    assert response.status_code == 404


def test_duplicate_workspace_membership_returns_conflict(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        member = register_and_login(client, "member@example.com")
        owner = login_existing_user(client, "owner@example.com")
        create_membership(client, workspace_id, owner, member.email)

        response = client.post(
            f"/api/v1/workspaces/{workspace_id}/memberships",
            json={"email": member.email, "role": "member"},
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 409


def test_owner_can_change_member_role(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        member = register_and_login(client, "member@example.com")
        owner = login_existing_user(client, "owner@example.com")
        membership = create_membership(client, workspace_id, owner, member.email)

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/memberships/{membership['id']}",
            json={"role": "admin"},
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_admin_cannot_change_member_role(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        admin = register_and_login(client, "admin@example.com")
        member = register_and_login(client, "member@example.com")
        owner = login_existing_user(client, "owner@example.com")
        create_membership(client, workspace_id, owner, admin.email, role="admin")
        membership = create_membership(client, workspace_id, owner, member.email)
        admin = login_existing_user(client, "admin@example.com")

        response = client.patch(
            f"/api/v1/workspaces/{workspace_id}/memberships/{membership['id']}",
            json={"role": "admin"},
            headers={"X-CSRF-Token": admin.csrf_token},
        )

    assert response.status_code == 403


def test_admin_can_remove_member_membership(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        admin = register_and_login(client, "admin@example.com")
        member = register_and_login(client, "member@example.com")
        owner = login_existing_user(client, "owner@example.com")
        create_membership(client, workspace_id, owner, admin.email, role="admin")
        membership = create_membership(client, workspace_id, owner, member.email)
        admin = login_existing_user(client, "admin@example.com")

        response = client.delete(
            f"/api/v1/workspaces/{workspace_id}/memberships/{membership['id']}",
            headers={"X-CSRF-Token": admin.csrf_token},
        )

    assert response.status_code == 204


def test_cannot_remove_last_workspace_owner(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        memberships = client.get(f"/api/v1/workspaces/{workspace_id}/memberships")
        assert memberships.status_code == 200
        owner_membership = next(
            membership
            for membership in memberships.json()
            if membership["email"] == "owner@example.com"
        )

        response = client.delete(
            f"/api/v1/workspaces/{workspace_id}/memberships/{owner_membership['id']}",
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert response.status_code == 409


def test_workspace_task_stale_version_returns_conflict(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        owner = register_and_login(client, "owner@example.com")
        workspace_id = create_workspace(client, owner)
        project = create_workspace_project(client, workspace_id, owner)
        task = create_workspace_task(client, workspace_id, project["id"], owner)

        first = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}",
            json={"title": "First update", "expected_version": task["version"]},
            headers={"X-CSRF-Token": owner.csrf_token},
        )
        stale = client.patch(
            f"/api/v1/workspaces/{workspace_id}/projects/{project['id']}"
            f"/tasks/{task['id']}",
            json={"title": "Stale update", "expected_version": task["version"]},
            headers={"X-CSRF-Token": owner.csrf_token},
        )

    assert first.status_code == 200
    assert first.json()["version"] == task["version"] + 1
    assert stale.status_code == 409
    assert stale.json()["error"]["code"] == "stale_task_version"
