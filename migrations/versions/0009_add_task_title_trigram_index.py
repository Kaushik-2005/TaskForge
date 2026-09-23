"""add trigram index for task title substring search

Revision ID: 0009_task_title_trigram
Revises: 0008_retries_artifacts
Create Date: 2026-09-23
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0009_task_title_trigram"
down_revision: str | None = "0008_retries_artifacts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE INDEX ix_tasks_title_trgm
        ON tasks USING gin (title gin_trgm_ops)
        """
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_title_trgm", table_name="tasks")
