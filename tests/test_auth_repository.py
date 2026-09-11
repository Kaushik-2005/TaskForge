from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from taskforge.auth_repository import AuthRepository
from taskforge.security import hash_token


def make_repo(database_url: str) -> tuple:
    engine = create_engine(database_url)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    return engine, session, AuthRepository(session)


def test_create_and_find_user_by_email(migrated_database_url: str) -> None:
    engine, session, repo = make_repo(migrated_database_url)
    try:
        created = repo.create_user(
            email="user@example.com",
            password_hash="hashed-password",
        )
        session.commit()

        found = repo.get_user_by_email("user@example.com")

        assert found is not None
        assert found.id == created.id
        assert found.email == "user@example.com"
        assert found.password_hash == "hashed-password"
    finally:
        session.close()
        engine.dispose()


def test_active_session_resolves_user(migrated_database_url: str) -> None:
    engine, session, repo = make_repo(migrated_database_url)
    try:
        user = repo.create_user(
            email="session@example.com",
            password_hash="hashed-password",
        )
        repo.create_session(
            user_id=user.id,
            session_token_hash=hash_token("session-token"),
            csrf_token_hash=hash_token("csrf-token"),
            ttl=timedelta(minutes=30),
        )
        session.commit()

        current_user = repo.get_active_user_for_session(
            session_token_hash=hash_token("session-token"),
            now=datetime.now(UTC),
        )

        assert current_user is not None
        assert current_user.id == user.id
        assert current_user.email == "session@example.com"
    finally:
        session.close()
        engine.dispose()


def test_expired_session_does_not_resolve_user(migrated_database_url: str) -> None:
    engine, session, repo = make_repo(migrated_database_url)
    try:
        user = repo.create_user(
            email="expired@example.com",
            password_hash="hashed-password",
        )
        repo.create_session(
            user_id=user.id,
            session_token_hash=hash_token("expired-session-token"),
            csrf_token_hash=hash_token("csrf-token"),
            ttl=timedelta(seconds=-1),
        )
        session.commit()

        current_user = repo.get_active_user_for_session(
            session_token_hash=hash_token("expired-session-token"),
            now=datetime.now(UTC),
        )

        assert current_user is None
    finally:
        session.close()
        engine.dispose()


def test_revoked_session_does_not_resolve_user(migrated_database_url: str) -> None:
    engine, session, repo = make_repo(migrated_database_url)
    try:
        user = repo.create_user(
            email="revoked@example.com",
            password_hash="hashed-password",
        )
        repo.create_session(
            user_id=user.id,
            session_token_hash=hash_token("revoked-session-token"),
            csrf_token_hash=hash_token("csrf-token"),
            ttl=timedelta(minutes=30),
        )
        session.commit()

        repo.revoke_session(hash_token("revoked-session-token"))
        session.commit()

        current_user = repo.get_active_user_for_session(
            session_token_hash=hash_token("revoked-session-token"),
            now=datetime.now(UTC),
        )

        assert current_user is None
    finally:
        session.close()
        engine.dispose()


def test_revoke_missing_session_returns_false(migrated_database_url: str) -> None:
    engine, session, repo = make_repo(migrated_database_url)
    try:
        result = repo.revoke_session(hash_token("missing-token"))

        assert result is False
    finally:
        session.close()
        engine.dispose()
