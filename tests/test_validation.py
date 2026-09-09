from fastapi.testclient import TestClient

from taskforge.main import create_app


def make_client() -> TestClient:
    return TestClient(create_app())


def create_project(client: TestClient) -> dict[str, str]:
    response = client.post("/api/v1/projects", json={"name": "Launch plan"})
    assert response.status_code == 201
    return response.json()


def create_task(client: TestClient, project_id: str) -> dict[str, str]:
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": "Draft checklist", "status": "todo"},
    )
    assert response.status_code == 201
    return response.json()


def test_malformed_json_is_reported_as_validation_error() -> None:
    client = make_client()

    response = client.post(
        "/api/v1/projects",
        content='{name: "Launch plan"}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["details"][0]["type"] == "json_invalid"


def test_unknown_project_create_field_is_rejected() -> None:
    client = make_client()

    response = client.post(
        "/api/v1/projects",
        json={"name": "Launch plan", "is_admin": True},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_unknown_task_update_field_is_rejected() -> None:
    client = make_client()
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"title": "Draft checklist", "priority": "high"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_patch_requires_at_least_one_field() -> None:
    client = make_client()
    project = create_project(client)

    response = client.patch(f"/api/v1/projects/{project['id']}", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_null_project_name_is_rejected_but_missing_task_title_is_allowed() -> None:
    client = make_client()
    project = create_project(client)
    task = create_task(client, project["id"])

    project_response = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": None},
    )
    assert project_response.status_code == 422

    task_response = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"status": "in_progress"},
    )
    assert task_response.status_code == 200
    assert task_response.json()["title"] == "Draft checklist"
    assert task_response.json()["status"] == "in_progress"


def test_task_cannot_jump_from_todo_to_done() -> None:
    client = make_client()
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"status": "done"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "invalid_state_transition",
            "message": "Task status cannot change directly from todo to done",
        }
    }


def test_task_can_move_from_todo_to_in_progress_to_done() -> None:
    client = make_client()
    project = create_project(client)
    task = create_task(client, project["id"])

    first = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"status": "in_progress"},
    )
    assert first.status_code == 200

    second = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"status": "done"},
    )
    assert second.status_code == 200
    assert second.json()["status"] == "done"


def test_path_ids_must_be_valid_uuid_shape() -> None:
    client = make_client()

    response = client.get("/api/v1/projects/not-a-uuid")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_response_does_not_include_unmodeled_internal_fields() -> None:
    client = make_client()

    response = client.post("/api/v1/projects", json={"name": "Launch plan"})

    assert response.status_code == 201
    assert set(response.json()) == {"id", "name", "created_at"}


def test_null_task_title_is_rejected_even_with_other_changes() -> None:
    client = make_client()
    project = create_project(client)
    task = create_task(client, project["id"])

    response = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={"title": None, "status": "in_progress"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
