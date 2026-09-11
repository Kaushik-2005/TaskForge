from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from taskforge.db_models import SessionRow, UserRow
from taskforge.models import UserRead


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_user(self, email: str, password_hash: str) -> UserRead:
        user = UserRow(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
        )
        self.session.add(user)
        self.session.flush()
        return self._user_read(user)

    def get_user_by_email(self, email: str) -> UserRow | None:
        return self.session.scalar(select(UserRow).where(UserRow.email == email))

    def create_session(
        self,
        user_id: UUID,
        session_token_hash: str,
        csrf_token_hash: str,
        ttl: timedelta,
    ) -> None:
        session = SessionRow(
            id=uuid4(),
            user_id=user_id,
            session_token_hash=session_token_hash,
            csrf_token_hash=csrf_token_hash,
            expires_at=datetime.now(UTC) + ttl,
        )
        self.session.add(session)
        self.session.flush()

    def revoke_session(self, session_token_hash: str) -> bool:
        session_row = self.session.scalar(
            select(SessionRow).where(
                SessionRow.session_token_hash == session_token_hash
            )
        )
        if session_row is None or session_row.revoked_at is not None:
            return False

        session_row.revoked_at = datetime.now(UTC)
        self.session.flush()
        return True

    def get_active_user_for_session(
        self,
        session_token_hash: str,
        now: datetime,
    ) -> UserRead | None:
        row = self.session.scalar(
            select(UserRow)
            .join(SessionRow, SessionRow.user_id == UserRow.id)
            .where(
                SessionRow.session_token_hash == session_token_hash,
                SessionRow.revoked_at.is_(None),
                SessionRow.expires_at > now,
            )
        )
        if row is None:
            return None
        return self._user_read(row)

    def active_session_has_csrf_token(
        self,
        session_token_hash: str,
        csrf_token_hash: str,
        now: datetime,
    ) -> bool:
        session_row = self.session.scalar(
            select(SessionRow).where(
                SessionRow.session_token_hash == session_token_hash,
                SessionRow.csrf_token_hash == csrf_token_hash,
                SessionRow.revoked_at.is_(None),
                SessionRow.expires_at > now,
            )
        )
        return session_row is not None

    @staticmethod
    def _user_read(row: UserRow) -> UserRead:
        return UserRead(id=row.id, email=row.email, created_at=row.created_at)
