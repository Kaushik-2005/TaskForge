"""add idempotency keys and move job export relationship

Revision ID: 0007_idempotency_export_link
Revises: 0006_add_job_leases
Create Date: 2026-09-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_idempotency_export_link"
down_revision: str | None = "0006_add_job_leases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add the new relationship temporarily as nullable
    op.add_column(
        "jobs",
        sa.Column(
            "export_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # 2. Copy the existing exports.job_id relationship
    op.execute(
        """
        UPDATE jobs
        SET export_id = exports.id
        FROM exports
        WHERE exports.job_id = jobs.id
        """
    )

    # 3. Every existing job must now have an export
    op.alter_column(
        "jobs",
        "export_id",
        nullable=False,
    )

    # 4. Enforce one job per export
    op.create_unique_constraint(
        "uq_jobs_export_id",
        "jobs",
        ["export_id"],
    )

    op.create_foreign_key(
        "fk_jobs_export_id",
        "jobs",
        "exports",
        ["export_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 5. Remove the old relationship
    op.drop_constraint(
        "exports_job_id_fkey",
        "exports",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_exports_job_id",
        "exports",
        type_="unique",
    )
    op.drop_column("exports", "job_id")

    # 6. Add idempotency storage
    op.create_table(
        "idempotency_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("export_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["export_id"],
            ["exports.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "user_id",
            "key",
            name="uq_idempotency_keys_user_key",
        ),
    )


def downgrade() -> None:
    # Remove idempotency storage first.
    op.drop_table("idempotency_keys")

    # Recreate the old exports.job_id column temporarily.
    op.add_column(
        "exports",
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Copy the relationship back.
    op.execute(
        """
        UPDATE exports
        SET job_id = jobs.id
        FROM jobs
        WHERE jobs.export_id = exports.id
        """
    )

    op.alter_column(
        "exports",
        "job_id",
        nullable=False,
    )

    op.create_foreign_key(
        "exports_job_id_fkey",
        "exports",
        "jobs",
        ["job_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_unique_constraint(
        "uq_exports_job_id",
        "exports",
        ["job_id"],
    )

    # Remove the new jobs.export_id relationship.
    op.drop_constraint(
        "fk_jobs_export_id",
        "jobs",
        type_="foreignkey",
    )
    op.drop_constraint(
        "uq_jobs_export_id",
        "jobs",
        type_="unique",
    )
    op.drop_column("jobs", "export_id")
