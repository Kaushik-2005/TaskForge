from __future__ import annotations

import argparse
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy.dialects.postgresql import insert

from taskforge.config import Settings
from taskforge.db import create_db_engine, create_session_factory
from taskforge.db_models import (
    MembershipRow,
    ProjectRow,
    TaskRow,
    UserRow,
    WorkspaceRow,
)
from taskforge.security import hash_password

LOAD_PASSWORD = "load-test-password"
LOAD_EMAIL_PREFIX = "load-user-"


def stable_id(kind: str, *parts: object) -> UUID:
    value = ":".join(("taskforge-load", kind, *(str(part) for part in parts)))
    return uuid5(NAMESPACE_URL, value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed deterministic TaskForge load data"
    )
    parser.add_argument("--workspaces", type=int, default=20)
    parser.add_argument("--projects-per-workspace", type=int, default=20)
    parser.add_argument("--tasks-per-project", type=int, default=100)
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".dist/load-test.env.ps1"),
        help="PowerShell file that receives the generated load-test variables",
    )
    return parser.parse_args()


def seed_load_data(
    args: argparse.Namespace,
) -> tuple[list[str], list[UUID], list[UUID]]:
    settings = Settings()
    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)
    password_hash = hash_password(LOAD_PASSWORD)

    user_rows = [
        {
            "id": stable_id("user", index),
            "email": f"{LOAD_EMAIL_PREFIX}{index:03d}@example.com",
            "password_hash": password_hash,
        }
        for index in range(args.users)
    ]
    workspace_rows = [
        {
            "id": stable_id("workspace", index),
            "name": f"Load Workspace {index:03d}",
        }
        for index in range(args.workspaces)
    ]
    project_rows = [
        {
            "id": stable_id("project", workspace_index, project_index),
            "workspace_id": stable_id("workspace", workspace_index),
            "name": f"Load Project {workspace_index:03d}-{project_index:03d}",
        }
        for workspace_index in range(args.workspaces)
        for project_index in range(args.projects_per_workspace)
    ]
    membership_rows = [
        {
            "id": stable_id("membership", user_index, workspace_index),
            "user_id": stable_id("user", user_index),
            "workspace_id": stable_id("workspace", workspace_index),
            "role": "owner" if user_index == 0 else "member",
        }
        for user_index in range(args.users)
        for workspace_index in range(args.workspaces)
    ]

    with session_factory.begin() as session:
        session.execute(
            insert(UserRow)
            .values(user_rows)
            .on_conflict_do_update(
                index_elements=[UserRow.email],
                set_={"password_hash": password_hash},
            )
        )
        session.execute(
            insert(WorkspaceRow)
            .values(workspace_rows)
            .on_conflict_do_nothing(index_elements=[WorkspaceRow.id])
        )
        session.execute(
            insert(MembershipRow)
            .values(membership_rows)
            .on_conflict_do_nothing(
                index_elements=[MembershipRow.user_id, MembershipRow.workspace_id]
            )
        )
        session.execute(
            insert(ProjectRow)
            .values(project_rows)
            .on_conflict_do_nothing(index_elements=[ProjectRow.id])
        )

        for project in project_rows:
            task_rows = [
                {
                    "id": stable_id("task", project["id"], task_index),
                    "project_id": project["id"],
                    "title": f"Load task {task_index:03d}",
                    "status": "todo",
                }
                for task_index in range(args.tasks_per_project)
            ]
            session.execute(
                insert(TaskRow)
                .values(task_rows)
                .on_conflict_do_nothing(index_elements=[TaskRow.id])
            )

    engine.dispose()
    credentials = [f"{row['email']}:{LOAD_PASSWORD}" for row in user_rows]
    workspace_ids = [row["id"] for row in workspace_rows]
    project_ids = [row["id"] for row in project_rows]
    return credentials, workspace_ids, project_ids


def main() -> None:
    args = parse_args()
    if (
        min(
            args.workspaces,
            args.projects_per_workspace,
            args.tasks_per_project,
            args.users,
        )
        < 1
    ):
        raise SystemExit("All seed counts must be positive")

    credentials, workspace_ids, project_ids = seed_load_data(args)
    print(f"Seeded {len(workspace_ids)} workspaces.")
    print(f"Seeded {len(project_ids)} projects.")
    task_count = args.workspaces * args.projects_per_workspace * args.tasks_per_project
    print(f"Seeded {task_count} tasks.")
    print(f"TASKFORGE_LOAD_USERS={','.join(credentials)}")
    print(f"TASKFORGE_LOAD_WORKSPACE_ID={workspace_ids[0]}")
    print(f"TASKFORGE_LOAD_PROJECT_ID={project_ids[0]}")

    args.env_file.parent.mkdir(parents=True, exist_ok=True)
    args.env_file.write_text(
        "\n".join(
            [
                f'$env:TASKFORGE_LOAD_USERS = "{",".join(credentials)}"',
                f'$env:TASKFORGE_LOAD_WORKSPACE_ID = "{workspace_ids[0]}"',
                f'$env:TASKFORGE_LOAD_PROJECT_ID = "{project_ids[0]}"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote PowerShell environment file: {args.env_file}")


if __name__ == "__main__":
    main()
