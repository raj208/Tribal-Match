from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.users.models import User

AUTH_ME_PATH = f"{settings.api_v1_prefix}/auth/me"
PROFILE_ME_PATH = f"{settings.api_v1_prefix}/profile/me"
SETTINGS_ME_PATH = f"{settings.api_v1_prefix}/settings/me"
INTERESTS_SENT_PATH = f"{settings.api_v1_prefix}/interests/sent"


def _auth_headers(email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer test-token:{email}"}


def _create_user(
    db: Session,
    email: str,
    *,
    supabase_user_id: str | None = None,
) -> User:
    user = User(email=email, supabase_user_id=supabase_user_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def test_valid_bearer_token_resolves_existing_authenticated_user(client, db_session: Session) -> None:
    user = _create_user(
        db_session,
        "resolved@example.com",
        supabase_user_id="test-supabase:resolved@example.com",
    )

    response = client.get(
        AUTH_ME_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert response.json()["supabase_user_id"] == "test-supabase:resolved@example.com"
    assert response.json()["email"] == "resolved@example.com"


def test_invalid_bearer_token_is_rejected_on_protected_route(client) -> None:
    response = client.get(
        SETTINGS_ME_PATH,
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired bearer token"}


def test_missing_bearer_token_is_rejected_on_protected_route(client) -> None:
    response = client.get(PROFILE_ME_PATH)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_existing_email_user_is_linked_to_verified_supabase_identity(
    client,
    db_session: Session,
) -> None:
    user = _create_user(db_session, "legacy@example.com")

    response = client.get(
        AUTH_ME_PATH,
        headers=_auth_headers(user.email),
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)
    assert response.json()["supabase_user_id"] == "test-supabase:legacy@example.com"

    db_session.expire_all()
    refreshed_user = db_session.get(User, user.id)
    assert refreshed_user is not None
    assert refreshed_user.supabase_user_id == "test-supabase:legacy@example.com"


def test_first_time_authenticated_user_is_created_from_verified_identity(
    client,
    db_session: Session,
) -> None:
    response = client.get(
        AUTH_ME_PATH,
        headers=_auth_headers("first-time@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["supabase_user_id"] == "test-supabase:first-time@example.com"
    assert response.json()["email"] == "first-time@example.com"

    user = _get_user_by_email(db_session, "first-time@example.com")
    assert user is not None
    assert user.supabase_user_id == "test-supabase:first-time@example.com"


def test_profile_settings_and_interests_accept_bearer_token_without_extra_identity_header(client) -> None:
    headers = _auth_headers("protected-flow@example.com")

    profile_response = client.get(PROFILE_ME_PATH, headers=headers)
    settings_response = client.get(SETTINGS_ME_PATH, headers=headers)
    interests_response = client.get(INTERESTS_SENT_PATH, headers=headers)

    assert profile_response.status_code == 404
    assert profile_response.json() == {"detail": "Profile not found"}

    assert settings_response.status_code == 200
    assert settings_response.json()["email"] == "protected-flow@example.com"
    assert settings_response.json()["profile_exists"] is False

    assert interests_response.status_code == 200
    assert interests_response.json() == []
