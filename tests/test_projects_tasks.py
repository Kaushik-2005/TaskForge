from fastapi.testclient import TestClient

from taskforge.config import Settings
from taskforge.main import create_app


def make_client() -> TestClient:
    return TestClient(
        create_app(Settings(environment="test", storage_backend="memory"))
    )


def create_project(client: TestClient, name: str = "Launch plan") -> dict[str, str]:
    response = client.post("/api/v1/projects", json={"name": name})
    assert response.status_code == 201
    return response.json()


def create_task(
    client: TestClient,
    project_id: str,
    title: str = "Draft checklist",
) -> dict[str, str]:
    response = client.post(
        f"/api/v1/projects/{project_id}/tasks",
        json={"title": title},
    )
    assert response.status_code == 201
    return response.json()


def test_project_crud_contract() -> None:
    client = make_client()

    create_response = client.post("/api/v1/projects", json={"name": "Launch plan"})
    assert create_response.status_code == 201
    assert create_response.headers["location"].startswith("/api/v1/projects/")
    project = create_response.json()

    list_response = client.get("/api/v1/projects")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [project["id"]]

    get_response = client.get(f"/api/v1/projects/{project['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Launch plan"

    update_response = client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"name": "Updated launch plan"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated launch plan"

    delete_response = client.delete(f"/api/v1/projects/{project['id']}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get(f"/api/v1/projects/{project['id']}")
    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "error": {"code": "not_found", "message": "Project not found"}
    }


def test_project_list_page_size_is_bounded() -> None:
    client = make_client()

    for index in range(3):
        create_project(client, name=f"Project {index}")

    response = client.get("/api/v1/projects?page_size=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    too_large = client.get("/api/v1/projects?page_size=101")
    assert too_large.status_code == 422
    assert too_large.json()["error"]["code"] == "validation_error"

    too_small = client.get("/api/v1/projects?page_size=0")
    assert too_small.status_code == 422
    assert too_small.json()["error"]["code"] == "validation_error"


def test_project_list_filters_by_name_case_insensitively() -> None:
    client = make_client()

    create_project(client, name="Launch plan")
    create_project(client, name="Backend work")
    create_project(client, name="PLAN review")

    response = client.get("/api/v1/projects?name_contains=plan")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == [
        "Launch plan",
        "PLAN review",
    ]


def test_project_list_filter_respects_page_size() -> None:
    client = make_client()

    create_project(client, name="Launch plan")
    create_project(client, name="Planning notes")
    create_project(client, name="PLAN review")
    create_project(client, name="Backend work")

    response = client.get("/api/v1/projects?name_contains=plan&page_size=2")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all("plan" in item["name"].lower() for item in response.json())


def test_project_list_filter_excludes_non_matching_projects() -> None:
    client = make_client()

    create_project(client, name="Backend work")

    response = client.get("/api/v1/projects?name_contains=plan")

    assert response.status_code == 200
    assert response.json() == []


def test_project_name_filter_rejects_empty_value() -> None:
    client = make_client()

    response = client.get("/api/v1/projects?name_contains=")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_wrong_method_returns_error_envelope() -> None:
    client = make_client()

    response = client.put("/api/v1/projects")

    assert response.status_code == 405
    assert response.json()["error"]["code"] == "http_error"


def test_task_crud_is_nested_under_project() -> None:
    client = make_client()
    project = create_project(client)

    create_response = client.post(
        f"/api/v1/projects/{project['id']}/tasks",
        json={"title": "Draft checklist", "status": "todo"},
    )
    assert create_response.status_code == 201
    assert create_response.headers["location"].startswith(
        f"/api/v1/projects/{project['id']}/tasks/"
    )
    task = create_response.json()
    assert task["project_id"] == project["id"]

    list_response = client.get(f"/api/v1/projects/{project['id']}/tasks")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [task["id"]]

    get_response = client.get(f"/api/v1/projects/{project['id']}/tasks/{task['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Draft checklist"

    update_response = client.patch(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}",
        json={
            "title": "Ship checklist",
            "status": "in_progress",
            "expected_version": task["version"],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Ship checklist"
    assert update_response.json()["status"] == "in_progress"

    delete_response = client.delete(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}"
    )
    assert delete_response.status_code == 204

    missing_response = client.get(
        f"/api/v1/projects/{project['id']}/tasks/{task['id']}"
    )
    assert missing_response.status_code == 404
    assert missing_response.json() == {
        "error": {"code": "not_found", "message": "Task not found"}
    }


def test_task_routes_require_existing_project_and_bounded_page_size() -> None:
    client = make_client()

    missing_project = client.post(
        "/api/v1/projects/00000000-0000-4000-8000-000000000001/tasks",
        json={"title": "No parent"},
    )
    assert missing_project.status_code == 404
    assert missing_project.json() == {
        "error": {"code": "not_found", "message": "Project not found"}
    }

    project = create_project(client)
    create_task(client, project["id"], "First")
    create_task(client, project["id"], "Second")

    limited = client.get(f"/api/v1/projects/{project['id']}/tasks?page_size=1")
    assert limited.status_code == 200
    assert len(limited.json()) == 1

    too_large = client.get(f"/api/v1/projects/{project['id']}/tasks?page_size=101")
    assert too_large.status_code == 422
    assert too_large.json()["error"]["code"] == "validation_error"


def test_nested_task_item_routes_report_missing_parent_project() -> None:
    client = make_client()

    response = client.get(
        "/api/v1/projects/00000000-0000-4000-8000-000000000001/tasks/00000000-0000-4000-8000-000000000002"
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Project not found"}
    }


def test_openapi_contract_includes_day_2_routes() -> None:
    client = make_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/projects" in paths
    assert "/api/v1/projects/{project_id}" in paths
    assert "/api/v1/projects/{project_id}/tasks" in paths
    assert "/api/v1/projects/{project_id}/tasks/{task_id}" in paths
