from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from test_auth_api import make_settings
from test_authorization import create_workspace, register_and_login

from taskforge.main import create_app
from taskforge.realtime import WorkspaceUpdateBroker


def test_authorized_workspace_websocket_receives_update(
    migrated_database_url: str,
) -> None:
    app = create_app(make_settings(migrated_database_url))

    with TestClient(app) as client:
        owner = register_and_login(client, "realtime-owner@example.com")
        workspace_id = create_workspace(client, owner)

        with client.websocket_connect(
            f"/api/v1/workspaces/{workspace_id}/updates",
            headers={"Origin": "http://testserver"},
        ) as websocket:
            event = {
                "type": "task.updated",
                "workspace_id": workspace_id,
                "task_id": "task-1",
            }
            app.state.workspace_update_broker.publish(
                UUID(workspace_id),
                event,
            )

            assert websocket.receive_json() == event


def test_outsider_cannot_subscribe_to_workspace_updates(
    migrated_database_url: str,
) -> None:
    app = create_app(make_settings(migrated_database_url))

    with TestClient(app) as client:
        owner = register_and_login(client, "realtime-owner-2@example.com")
        workspace_id = create_workspace(client, owner)
        register_and_login(client, "realtime-outsider@example.com")

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(
                f"/api/v1/workspaces/{workspace_id}/updates",
                headers={"Origin": "http://testserver"},
            ):
                pass

    assert exc_info.value.code == 1008


def test_disallowed_websocket_origin_is_rejected(
    migrated_database_url: str,
) -> None:
    app = create_app(make_settings(migrated_database_url))

    with TestClient(app) as client:
        owner = register_and_login(client, "realtime-owner-3@example.com")
        workspace_id = create_workspace(client, owner)

        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect(
                f"/api/v1/workspaces/{workspace_id}/updates",
                headers={"Origin": "https://evil.example"},
            ):
                pass

    assert exc_info.value.code == 1008


def test_workspace_update_broker_bounds_slow_consumer_queue() -> None:
    broker = WorkspaceUpdateBroker(queue_size=1)
    workspace_id = UUID("00000000-0000-4000-8000-000000000001")
    queue = broker.subscribe(workspace_id)

    broker.publish(workspace_id, {"type": "task.updated", "version": 1})
    broker.publish(workspace_id, {"type": "task.updated", "version": 2})

    assert queue.qsize() == 1
    assert queue.get_nowait() == {
        "type": "resync_required",
        "workspace_id": str(workspace_id),
    }
