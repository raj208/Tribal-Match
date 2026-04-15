import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import SupabaseTokenVerificationError, verify_supabase_access_token
from app.modules.users.models import User

AUTH_ME_PATH = f"{settings.api_v1_prefix}/auth/me"
AUTH_DEBUG_ME_PATH = f"{settings.api_v1_prefix}/auth/_debug/me"


def _verified_claims(
    *,
    sub: str = "supabase-user-id",
    email: str = "token-user@example.com",
) -> dict[str, object]:
    return {
        "sub": sub,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "https://project-ref.supabase.co/auth/v1",
        "exp": 1_800_000_000,
        "iat": 1_700_000_000,
        "session_id": "session-id",
        "aal": "aal1",
        "is_anonymous": False,
    }


def _stub_verified_token(monkeypatch: pytest.MonkeyPatch, claims: dict[str, object]) -> None:
    def fake_verify_supabase_access_token(token: str) -> dict[str, object]:
        assert token == "valid-token"
        return claims

    monkeypatch.setattr(
        "app.modules.auth.dependencies.verify_supabase_access_token",
        fake_verify_supabase_access_token,
    )


def _get_user_by_supabase_user_id(db: Session, supabase_user_id: str) -> User | None:
    return db.scalar(select(User).where(User.supabase_user_id == supabase_user_id))


def test_auth_debug_me_requires_bearer_token(client) -> None:
    response = client.get(AUTH_DEBUG_ME_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token required"}


def test_auth_debug_me_returns_verified_token_identity(client, monkeypatch) -> None:
    _stub_verified_token(monkeypatch, _verified_claims())

    response = client.get(
        AUTH_DEBUG_ME_PATH,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "auth_source": "supabase_bearer",
        "sub": "supabase-user-id",
        "email": "token-user@example.com",
        "phone": None,
        "role": "authenticated",
        "aud": "authenticated",
        "iss": "https://project-ref.supabase.co/auth/v1",
        "exp": 1_800_000_000,
        "iat": 1_700_000_000,
        "session_id": "session-id",
        "aal": "aal1",
        "is_anonymous": False,
    }


def test_auth_debug_me_rejects_invalid_bearer_token(client, monkeypatch) -> None:
    def fake_verify_supabase_access_token(_: str) -> dict[str, object]:
        raise SupabaseTokenVerificationError("bad token")

    monkeypatch.setattr(
        "app.modules.auth.dependencies.verify_supabase_access_token",
        fake_verify_supabase_access_token,
    )

    response = client.get(
        AUTH_DEBUG_ME_PATH,
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired bearer token"}


def test_auth_me_requires_bearer_token(client) -> None:
    response = client.get(AUTH_ME_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_auth_me_uses_verified_bearer_token(client, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_verified_token(monkeypatch, _verified_claims())

    response = client.get(
        AUTH_ME_PATH,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json()["auth_source"] == "supabase_bearer"
    assert response.json()["supabase_user_id"] == "supabase-user-id"
    assert response.json()["email"] == "token-user@example.com"


def test_auth_me_returns_existing_user_by_supabase_identity(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = User(email="token-user@example.com", supabase_user_id="supabase-user-id")
    db_session.add(user)
    db_session.commit()

    _stub_verified_token(monkeypatch, _verified_claims())

    response = client.get(
        AUTH_ME_PATH,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json()["auth_source"] == "supabase_bearer"
    assert response.json()["email"] == "token-user@example.com"


def test_auth_me_links_existing_email_user_to_supabase_identity(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = User(email="legacy-token-user@example.com")
    db_session.add(user)
    db_session.commit()

    _stub_verified_token(
        monkeypatch,
        _verified_claims(sub="new-supabase-user-id", email="legacy-token-user@example.com"),
    )

    response = client.get(
        AUTH_ME_PATH,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "legacy-token-user@example.com"

    db_session.expire_all()
    refreshed_user = db_session.get(User, user.id)
    assert refreshed_user is not None
    assert refreshed_user.supabase_user_id == "new-supabase-user-id"


def test_auth_me_creates_user_from_verified_supabase_identity(
    client,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _stub_verified_token(
        monkeypatch,
        _verified_claims(sub="created-supabase-user-id", email="Created-Token-User@Example.com"),
    )

    response = client.get(
        AUTH_ME_PATH,
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "created-token-user@example.com"

    user = _get_user_by_supabase_user_id(db_session, "created-supabase-user-id")
    assert user is not None
    assert user.email == "created-token-user@example.com"


def test_auth_me_rejects_invalid_bearer_token(
    client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_verify_supabase_access_token(_: str) -> dict[str, object]:
        raise SupabaseTokenVerificationError("bad token")

    monkeypatch.setattr(
        "app.modules.auth.dependencies.verify_supabase_access_token",
        fake_verify_supabase_access_token,
    )

    response = client.get(
        AUTH_ME_PATH,
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired bearer token"}


def test_verify_supabase_access_token_validates_hs256_signature() -> None:
    jwt = pytest.importorskip("jwt")

    original_supabase_url = settings.supabase_url
    original_jwt_secret = settings.supabase_jwt_secret
    original_jwt_issuer = settings.supabase_jwt_issuer
    original_jwt_audience = settings.supabase_jwt_audience
    original_jwt_algorithms = settings.supabase_jwt_algorithms

    settings.supabase_url = "https://project-ref.supabase.co"
    settings.supabase_jwt_secret = "test-secret"
    settings.supabase_jwt_issuer = ""
    settings.supabase_jwt_audience = "authenticated"
    settings.supabase_jwt_algorithms = "HS256"

    try:
        token = jwt.encode(
            {
                "sub": "supabase-user-id",
                "email": "token-user@example.com",
                "aud": "authenticated",
                "iss": "https://project-ref.supabase.co/auth/v1",
                "exp": 1_800_000_000,
            },
            "test-secret",
            algorithm="HS256",
        )

        claims = verify_supabase_access_token(token)
    finally:
        settings.supabase_url = original_supabase_url
        settings.supabase_jwt_secret = original_jwt_secret
        settings.supabase_jwt_issuer = original_jwt_issuer
        settings.supabase_jwt_audience = original_jwt_audience
        settings.supabase_jwt_algorithms = original_jwt_algorithms

    assert claims["sub"] == "supabase-user-id"
    assert claims["email"] == "token-user@example.com"
