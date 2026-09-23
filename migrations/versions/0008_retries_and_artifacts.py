"""add retry state and artifact checksum

Revision ID: 0008_retries_artifacts
Revises: 0007_idempotency_export_link
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_retries_artifacts"
down_revision: str | None = "0007_idempotency_export_link"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "idempotency_keys",
        sa.Column(
            "workspace_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.add_column(
        "idempotency_keys",
        sa.Column(
            "operation",
            sa.String(length=50),
            server_default="workspace_export",
            nullable=False,
        ),
    )
    op.execute(
        """
        UPDATE idempotency_keys AS i
        SET workspace_id = e.workspace_id
        FROM exports AS e
        WHERE e.id = i.export_id
        """
    )
    op.alter_column(
        "idempotency_keys",
        "workspace_id",
        nullable=False,
    )
    op.create_foreign_key(
        "fk_idempotency_keys_workspace_id",
        "idempotency_keys",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "uq_idempotency_keys_user_key",
        "idempotency_keys",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_idempotency_keys_scope",
        "idempotency_keys",
        ["user_id", "workspace_id", "operation", "key"],
    )

    op.add_column(
        "jobs",
        sa.Column("attempt", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "jobs",
        sa.Column("max_attempts", sa.Integer(), server_default="3", nullable=False),
    )
    op.add_column(
        "jobs",
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "exports",
        sa.Column("output_checksum", sa.String(length=64), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("exports", "output_checksum")
    op.drop_column("jobs", "next_retry_at")
    op.drop_column("jobs", "max_attempts")
    op.drop_column("jobs", "attempt")
    op.drop_constraint(
        "uq_idempotency_keys_scope",
        "idempotency_keys",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_idempotency_keys_user_key",
        "idempotency_keys",
        ["user_id", "key"],
    )
    op.drop_constraint(
        "fk_idempotency_keys_workspace_id",
        "idempotency_keys",
        type_="foreignkey",
    )
    op.drop_column("idempotency_keys", "operation")
    op.drop_column("idempotency_keys", "workspace_id")
