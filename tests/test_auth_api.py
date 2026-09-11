from http.cookies import SimpleCookie

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text

from taskforge.config import Settings
from taskforge.main import create_app


def make_settings(url: str, *, secure_cookie: bool = False) -> Settings:
    return Settings(
        environment="test",
        storage_backend="postgres",
        database_url=url,
        database_pool_size=2,
        database_max_overflow=0,
        database_pool_timeout_seconds=2,
        session_cookie_secure=secure_cookie,
    )


def register_user(client: TestClient, email: str = "user@example.com") -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-password"},
    )
    assert response.status_code == 201


def login_user(client: TestClient, email: str = "user@example.com") -> tuple[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-password"},
    )
    assert response.status_code == 200
    csrf_token = response.json()["csrf_token"]
    session_token = client.cookies.get("taskforge_session")
    assert session_token is not None
    return session_token, csrf_token


def cookie_value(set_cookie: str, name: str) -> str:
    cookie = SimpleCookie()
    cookie.load(set_cookie)
    return cookie[name].value


def test_register_login_and_me(migrated_database_url: str) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        register_user(client)
        _session_token, _csrf_token = login_user(client)

        current = client.get("/api/v1/auth/me")

    assert current.status_code == 200
    assert current.json()["email"] == "user@example.com"


def test_wrong_credentials_return_401(migrated_database_url: str) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        register_user(client)

        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "wrong-password"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"
    assert "taskforge_session" not in response.cookies


def test_expired_session_cannot_read_me(migrated_database_url: str) -> None:
    engine = create_engine(migrated_database_url)
    try:
        with TestClient(create_app(make_settings(migrated_database_url))) as client:
            register_user(client)
            login_user(client)

            with engine.begin() as connection:
                connection.execute(
                    text("UPDATE sessions SET expires_at = now() - interval '1 minute'")
                )

            response = client.get("/api/v1/auth/me")
    finally:
        engine.dispose()

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthenticated"


def test_logout_revokes_session(migrated_database_url: str) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        register_user(client)
        session_token, csrf_token = login_user(client)

        logout = client.post(
            "/api/v1/auth/logout",
            headers={"X-CSRF-Token": csrf_token},
        )
        client.cookies.set("taskforge_session", session_token)
        current = client.get("/api/v1/auth/me")

    assert logout.status_code == 204
    assert current.status_code == 401


def test_login_rotates_session_cookie_value(migrated_database_url: str) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        register_user(client)
        first = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "correct-password"},
        )
        second = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "correct-password"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    first_cookie = cookie_value(first.headers["set-cookie"], "taskforge_session")
    second_cookie = cookie_value(second.headers["set-cookie"], "taskforge_session")
    assert first_cookie != second_cookie


def test_cookie_authenticated_mutation_requires_csrf(
    migrated_database_url: str,
) -> None:
    with TestClient(create_app(make_settings(migrated_database_url))) as client:
        register_user(client)
        _session_token, csrf_token = login_user(client)

        missing_csrf = client.post(
            "/api/v1/projects",
            json={"name": "Protected mutation"},
        )
        valid_csrf = client.post(
            "/api/v1/projects",
            json={"name": "Protected mutation"},
            headers={"X-CSRF-Token": csrf_token},
        )

    assert missing_csrf.status_code == 403
    assert missing_csrf.json()["error"]["code"] == "csrf_required"
    assert valid_csrf.status_code == 201


def test_release_profile_can_set_secure_session_cookie(
    migrated_database_url: str,
) -> None:
    with TestClient(
        create_app(make_settings(migrated_database_url, secure_cookie=True))
    ) as client:
        register_user(client)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "correct-password"},
        )

    assert response.status_code == 200
    set_cookie = response.headers["set-cookie"]
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Secure" in set_cookie
