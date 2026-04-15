import pytest

from app.core.config import settings
from app.core.security import SupabaseTokenVerificationError, verify_supabase_access_token

AUTH_ME_PATH = f"{settings.api_v1_prefix}/auth/me"
AUTH_DEBUG_ME_PATH = f"{settings.api_v1_prefix}/auth/_debug/me"


def test_auth_debug_me_requires_bearer_token_even_with_bridge_header(client) -> None:
    response = client.get(
        AUTH_DEBUG_ME_PATH,
        headers={"X-User-Email": "bridge@example.com"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Bearer token required"}


def test_auth_debug_me_returns_verified_token_identity(client, monkeypatch) -> None:
    def fake_verify_supabase_access_token(token: str) -> dict[str, object]:
        assert token == "valid-token"
        return {
            "sub": "supabase-user-id",
            "email": "token-user@example.com",
            "role": "authenticated",
            "aud": "authenticated",
            "iss": "https://project-ref.supabase.co/auth/v1",
            "exp": 1_800_000_000,
            "iat": 1_700_000_000,
            "session_id": "session-id",
            "aal": "aal1",
            "is_anonymous": False,
        }

    monkeypatch.setattr(
        "app.modules.auth.dependencies.verify_supabase_access_token",
        fake_verify_supabase_access_token,
    )

    response = client.get(
        AUTH_DEBUG_ME_PATH,
        headers={
            "Authorization": "Bearer valid-token",
            "X-User-Email": "bridge@example.com",
        },
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


def test_auth_me_still_uses_existing_bridge_header(client) -> None:
    response = client.get(
        AUTH_ME_PATH,
        headers={"X-User-Email": "bridge@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "bridge@example.com"


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
