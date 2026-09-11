from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from taskforge.auth_repository import AuthRepository
from taskforge.errors import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UnauthenticatedError,
)
from taskforge.models import UserRead
from taskforge.security import (
    generate_token,
    hash_password,
    hash_token,
    verify_password,
)


@dataclass(frozen=True)
class AuthSession:
    user: UserRead
    session_token: str
    csrf_token: str


class AuthService:
    def __init__(self, repository: AuthRepository, session_ttl: timedelta) -> None:
        self.repository = repository
        self.session_ttl = session_ttl

    def register(self, email: str, password: str) -> UserRead:
        normalized_email = self._normalize_email(email)
        if self.repository.get_user_by_email(normalized_email) is not None:
            raise EmailAlreadyRegisteredError
        return self.repository.create_user(
            email=normalized_email,
            password_hash=hash_password(password),
        )

    def login(self, email: str, password: str) -> AuthSession:
        normalized_email = self._normalize_email(email)
        user_row = self.repository.get_user_by_email(normalized_email)
        if user_row is None or not verify_password(password, user_row.password_hash):
            raise InvalidCredentialsError

        session_token = generate_token()
        csrf_token = generate_token()
        self.repository.create_session(
            user_id=user_row.id,
            session_token_hash=hash_token(session_token),
            csrf_token_hash=hash_token(csrf_token),
            ttl=self.session_ttl,
        )
        return AuthSession(
            user=UserRead(
                id=user_row.id,
                email=user_row.email,
                created_at=user_row.created_at,
            ),
            session_token=session_token,
            csrf_token=csrf_token,
        )

    def logout(self, session_token: str | None) -> None:
        if session_token is None:
            return
        self.repository.revoke_session(hash_token(session_token))

    def current_user(self, session_token: str | None) -> UserRead:
        if session_token is None:
            raise UnauthenticatedError
        user = self.repository.get_active_user_for_session(
            session_token_hash=hash_token(session_token),
            now=datetime.now(UTC),
        )
        if user is None:
            raise UnauthenticatedError
        return user

    def csrf_token_is_valid(self, session_token: str, csrf_token: str | None) -> bool:
        if csrf_token is None:
            return False
        return self.repository.active_session_has_csrf_token(
            session_token_hash=hash_token(session_token),
            csrf_token_hash=hash_token(csrf_token),
            now=datetime.now(UTC),
        )

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()
