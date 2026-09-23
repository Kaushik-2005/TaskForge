"""add job lease ownership

Revision ID: 0006_add_job_leases
Revises: 0005_add_exports_and_jobs
Create Date: 2026-09-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_add_job_leases"
down_revision: str | None = "0005_add_exports_and_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("owner_token", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "jobs",
        sa.Column("lease_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_jobs_status_lease_expires_at",
        "jobs",
        ["status", "lease_expires_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_status_lease_expires_at", table_name="jobs")
    op.drop_column("jobs", "lease_expires_at")
    op.drop_column("jobs", "owner_token")
