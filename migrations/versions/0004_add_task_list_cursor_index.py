"""add task list cursor index

Revision ID: 0004_add_task_list_cursor_index
Revises: 0003_task_versions_audit_events
Create Date: 2026-09-14
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004_add_task_list_cursor_index"
down_revision: str | None = "0003_task_versions_audit_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_tasks_project_created_at_id",
        "tasks",
        ["project_id", "created_at", "id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_project_created_at_id", table_name="tasks")
