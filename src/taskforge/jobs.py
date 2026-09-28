import csv
import hashlib
import json
import os
import random
import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import and_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from taskforge.db_models import (
    ExportRow,
    IdempotencyKeyRow,
    JobRow,
    MembershipRow,
    ProjectRow,
    TaskRow,
)
from taskforge.errors import (
    ExportArtifactMissingError,
    ExportExpiredError,
    ExportNotFoundError,
    ExportNotReadyError,
    IdempotencyConflictError,
    WorkspaceNotFoundError,
)
from taskforge.models import ExportRead, ExportStatus, UserRead

EXPORT_OPERATION = "workspace_export"


def export_request_hash(workspace_id: UUID) -> str:
    fingerprint_input = {
        "operation": EXPORT_OPERATION,
        "workspace_id": str(workspace_id),
        "body": {},
    }

    canonical = json.dumps(
        fingerprint_input,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class JobClaim:
    job_id: UUID
    export_id: UUID
    workspace_id: UUID
    owner_token: UUID
    attempt: int


class RetryableExportError(Exception):
    """An export failure that may succeed on a later attempt."""


class ExportService:
    def __init__(self, repository: "ExportRepository", storage_dir: str) -> None:
        self.repository = repository
        self.storage_dir = Path(storage_dir).resolve()

    def create_export(
        self,
        current_user: UserRead,
        workspace_id: UUID,
        idempotency_key: str,
    ) -> ExportRead:
        export = self.repository.create_idempotent_for_user(
            current_user.id,
            workspace_id,
            idempotency_key,
            export_request_hash(workspace_id),
        )
        if export is None:
            raise WorkspaceNotFoundError
        return export

    def get_export(
        self,
        current_user: UserRead,
        export_id: UUID,
    ) -> ExportRead:
        export = self.repository.get_for_user(current_user.id, export_id)
        if export is None:
            raise ExportNotFoundError
        return export

    def get_download_path(
        self,
        current_user: UserRead,
        export_id: UUID,
    ) -> Path:
        export = self.repository.get_for_user(current_user.id, export_id)
        if export is None:
            raise ExportNotFoundError
        if export.status != ExportStatus.succeeded:
            raise ExportNotReadyError
        if export.output_reference is None:
            raise ExportExpiredError

        output_path = safe_output_path(self.storage_dir, export.output_reference)
        if output_path is None:
            raise ExportArtifactMissingError
        if not output_path.is_file():
            raise ExportArtifactMissingError
        return output_path


def safe_output_path(storage_dir: Path, output_reference: str) -> Path | None:
    relative_reference = Path(output_reference)
    if relative_reference.parts[:1] == ("exports",):
        relative_reference = Path(*relative_reference.parts[1:])

    output_path = (storage_dir / relative_reference).resolve()
    try:
        output_path.relative_to(storage_dir)
    except ValueError:
        return None
    return output_path


def cleanup_expired_export_artifacts(
    session_factory: sessionmaker[Session],
    export_storage_dir: str,
    retention: timedelta,
) -> int:
    storage_dir = Path(export_storage_dir).resolve()
    cutoff = datetime.now(UTC) - retention
    removed = 0

    with session_factory() as session:
        exports = session.scalars(
            select(ExportRow).where(
                ExportRow.status == ExportStatus.succeeded.value,
                ExportRow.completed_at.is_not(None),
                ExportRow.completed_at < cutoff,
                ExportRow.output_location.is_not(None),
            )
        ).all()

        for export in exports:
            if export.output_location is not None:
                output_path = safe_output_path(storage_dir, export.output_location)
                if output_path is not None:
                    output_path.unlink(missing_ok=True)
            export.output_location = None
            export.output_checksum = None
            removed += 1

        session.commit()

    return removed


class ExportRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
    ) -> ExportRead | None:
        has_membership = self.session.scalar(
            select(MembershipRow.id).where(
                MembershipRow.user_id == user_id,
                MembershipRow.workspace_id == workspace_id,
            )
        )
        if has_membership is None:
            return None

        export = ExportRow(
            id=uuid4(),
            workspace_id=workspace_id,
            requested_by=user_id,
            status=ExportStatus.pending.value,
        )
        self.session.add(export)
        self.session.flush()

        job = JobRow(
            id=uuid4(),
            export_id=export.id,
            kind="export",
            status=ExportStatus.pending.value,
        )
        self.session.add(job)
        self.session.flush()
        return self._read(export)

    def _resolve_existing_idempotency(
        self,
        row: IdempotencyKeyRow,
        request_hash: str,
    ) -> ExportRead:
        if row.request_hash != request_hash:
            raise IdempotencyConflictError

        export = self.session.get(ExportRow, row.export_id)
        if export is None:
            raise ExportNotFoundError

        return self._read(export)

    def create_idempotent_for_user(
        self,
        user_id: UUID,
        workspace_id: UUID,
        idempotency_key: str,
        request_hash: str,
    ) -> ExportRead | None:
        has_membership = self.session.scalar(
            select(MembershipRow.id).where(
                MembershipRow.user_id == user_id,
                MembershipRow.workspace_id == workspace_id,
            )
        )
        if has_membership is None:
            return None

        existing = self.session.scalar(
            select(IdempotencyKeyRow).where(
                IdempotencyKeyRow.user_id == user_id,
                IdempotencyKeyRow.workspace_id == workspace_id,
                IdempotencyKeyRow.operation == EXPORT_OPERATION,
                IdempotencyKeyRow.key == idempotency_key,
            )
        )
        if existing is not None:
            return self._resolve_existing_idempotency(existing, request_hash)

        try:
            with self.session.begin_nested():
                export = ExportRow(
                    id=uuid4(),
                    workspace_id=workspace_id,
                    requested_by=user_id,
                    status=ExportStatus.pending.value,
                )
                self.session.add(export)
                self.session.flush()

                job = JobRow(
                    id=uuid4(),
                    export_id=export.id,
                    kind="export",
                    status=ExportStatus.pending.value,
                )
                self.session.add(job)
                self.session.flush()

                idempotency_row = IdempotencyKeyRow(
                    id=uuid4(),
                    user_id=user_id,
                    workspace_id=workspace_id,
                    operation=EXPORT_OPERATION,
                    key=idempotency_key,
                    request_hash=request_hash,
                    export_id=export.id,
                )
                self.session.add(idempotency_row)
                self.session.flush()
        except IntegrityError:
            existing = self.session.scalar(
                select(IdempotencyKeyRow).where(
                    IdempotencyKeyRow.user_id == user_id,
                    IdempotencyKeyRow.workspace_id == workspace_id,
                    IdempotencyKeyRow.operation == EXPORT_OPERATION,
                    IdempotencyKeyRow.key == idempotency_key,
                )
            )
            if existing is None:
                raise

            return self._resolve_existing_idempotency(existing, request_hash)

        return self._read(export)

    def get_for_user(
        self,
        user_id: UUID,
        export_id: UUID,
    ) -> ExportRead | None:
        row = self.session.scalar(
            select(ExportRow)
            .join(
                MembershipRow,
                MembershipRow.workspace_id == ExportRow.workspace_id,
            )
            .where(
                ExportRow.id == export_id,
                MembershipRow.user_id == user_id,
            )
        )
        return None if row is None else self._read(row)

    def claim_one(self, lease_seconds: int) -> JobClaim | None:
        now = datetime.now(UTC)
        job = self.session.scalar(
            select(JobRow)
            .where(
                JobRow.kind == "export",
                or_(
                    and_(
                        JobRow.status == ExportStatus.pending.value,
                        or_(
                            JobRow.next_retry_at.is_(None),
                            JobRow.next_retry_at <= now,
                        ),
                    ),
                    and_(
                        JobRow.status == ExportStatus.running.value,
                        JobRow.lease_expires_at <= now,
                    ),
                ),
            )
            .order_by(JobRow.created_at, JobRow.id)
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        if job is None:
            return None

        export = self.session.scalar(
            select(ExportRow).where(ExportRow.id == job.export_id)
        )
        if export is None:
            return None

        owner_token = uuid4()
        job.status = ExportStatus.running.value
        job.owner_token = owner_token
        job.lease_expires_at = now + timedelta(seconds=lease_seconds)
        job.started_at = now
        job.attempt += 1
        job.next_retry_at = None
        job.error = None
        export.status = ExportStatus.running.value
        self.session.flush()
        return JobClaim(
            job.id,
            export.id,
            export.workspace_id,
            owner_token,
            job.attempt,
        )

    def renew_lease(
        self,
        claim: JobClaim,
        lease_seconds: int,
    ) -> bool:
        result = self.session.execute(
            update(JobRow)
            .where(
                JobRow.id == claim.job_id,
                JobRow.status == ExportStatus.running.value,
                JobRow.owner_token == claim.owner_token,
            )
            .values(
                lease_expires_at=datetime.now(UTC) + timedelta(seconds=lease_seconds)
            )
        )
        return result.rowcount == 1

    def complete(
        self,
        claim: JobClaim,
        output_reference: str,
        output_checksum: str,
    ) -> bool:
        now = datetime.now(UTC)
        job_result = self.session.execute(
            update(JobRow)
            .where(
                JobRow.id == claim.job_id,
                JobRow.status == ExportStatus.running.value,
                JobRow.owner_token == claim.owner_token,
            )
            .values(
                status=ExportStatus.succeeded.value,
                completed_at=now,
                lease_expires_at=None,
                next_retry_at=None,
                error=None,
            )
        )
        if job_result.rowcount != 1:
            return False

        export_result = self.session.execute(
            update(ExportRow)
            .where(
                ExportRow.id == claim.export_id,
                ExportRow.status == ExportStatus.running.value,
            )
            .values(
                status=ExportStatus.succeeded.value,
                output_location=output_reference,
                output_checksum=output_checksum,
                completed_at=now,
                error=None,
            )
        )
        if export_result.rowcount != 1:
            return False
        self.session.flush()
        return True

    def fail_or_retry(
        self,
        claim: JobClaim,
        message: str,
        retryable: bool,
    ) -> bool:
        now = datetime.now(UTC)
        safe_message = message[:500]
        job = self.session.scalar(
            select(JobRow).where(
                JobRow.id == claim.job_id,
                JobRow.status == ExportStatus.running.value,
                JobRow.owner_token == claim.owner_token,
            )
        )
        if job is None:
            return False

        should_retry = retryable and job.attempt < job.max_attempts
        if should_retry:
            backoff_seconds = min(60, 2 ** max(0, job.attempt - 1))
            delay = backoff_seconds + random.uniform(0, 1)
            job.status = ExportStatus.pending.value
            job.completed_at = None
            job.lease_expires_at = None
            job.owner_token = None
            job.next_retry_at = now + timedelta(seconds=delay)
            job.error = safe_message
        else:
            job.status = ExportStatus.failed.value
            job.completed_at = now
            job.lease_expires_at = None
            job.owner_token = None
            job.next_retry_at = None
            job.error = safe_message

        export = self.session.get(ExportRow, claim.export_id)
        if export is None or export.status != ExportStatus.running.value:
            return False

        export.status = (
            ExportStatus.pending.value if should_retry else ExportStatus.failed.value
        )
        export.completed_at = None if should_retry else now
        export.error = safe_message
        self.session.flush()
        return True

    @staticmethod
    def _read(row: ExportRow) -> ExportRead:
        return ExportRead(
            id=row.id,
            workspace_id=row.workspace_id,
            status=ExportStatus(row.status),
            created_at=row.created_at,
            completed_at=row.completed_at,
            output_reference=row.output_location,
            error=row.error,
        )


def generate_workspace_csv(session: Session, workspace_id: UUID, path: Path) -> None:
    rows = session.execute(
        select(ProjectRow.name, TaskRow.title, TaskRow.status)
        .join(TaskRow, TaskRow.project_id == ProjectRow.id)
        .where(ProjectRow.workspace_id == workspace_id)
        .order_by(ProjectRow.id, TaskRow.created_at, TaskRow.id)
    ).all()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["project", "task", "status"])
        writer.writerows([csv_safe_cell(value) for value in row] for row in rows)


def csv_safe_cell(value: str) -> str:
    """Prevent spreadsheet applications from treating text as a formula."""
    if value.startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_one_export(
    session_factory: sessionmaker[Session],
    export_storage_dir: str,
    lease_seconds: int = 30,
    generator: Callable[[Session, UUID, Path], None] = generate_workspace_csv,
) -> bool:
    with session_factory() as session:
        repository = ExportRepository(session)
        claim = repository.claim_one(lease_seconds)
        if claim is None:
            return False
        session.commit()

        stop_heartbeat = threading.Event()
        lease_lost = threading.Event()

        def renew_until_stopped() -> None:
            interval = max(0.1, lease_seconds / 3)
            while not stop_heartbeat.wait(interval):
                with session_factory() as heartbeat_session:
                    heartbeat_repository = ExportRepository(heartbeat_session)
                    renewed = heartbeat_repository.renew_lease(claim, lease_seconds)
                    if renewed:
                        heartbeat_session.commit()
                    else:
                        heartbeat_session.rollback()
                        lease_lost.set()
                        return

        heartbeat = threading.Thread(target=renew_until_stopped, daemon=True)
        heartbeat.start()
        output_dir = Path(export_storage_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"export_{claim.export_id}_attempt_{claim.attempt}.csv"
        output_path = output_dir / filename
        temporary_path = output_dir / f".{filename}.{claim.owner_token}.tmp"
        try:
            generator(session, claim.workspace_id, temporary_path)
            if lease_lost.is_set():
                temporary_path.unlink(missing_ok=True)
                session.rollback()
                return True

            output_checksum = sha256_file(temporary_path)
            os.replace(temporary_path, output_path)

            if lease_lost.is_set():
                output_path.unlink(missing_ok=True)
                session.rollback()
                return True

            completed = repository.complete(
                claim,
                f"exports/{filename}",
                output_checksum,
            )
            if completed:
                session.commit()
            else:
                session.rollback()
                output_path.unlink(missing_ok=True)
        except Exception as exc:
            temporary_path.unlink(missing_ok=True)
            session.rollback()
            retryable = isinstance(exc, (RetryableExportError, OSError, TimeoutError))
            if repository.fail_or_retry(claim, "Export generation failed", retryable):
                session.commit()
            else:
                session.rollback()
        finally:
            temporary_path.unlink(missing_ok=True)
            stop_heartbeat.set()
            heartbeat.join()
        return True
